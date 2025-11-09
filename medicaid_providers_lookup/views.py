from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from collections import OrderedDict
from django.core.paginator import Paginator


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [OrderedDict(zip(columns, row)) for row in cursor.fetchall()]


def search_providers(request):
    try:
        with connection.cursor() as cursor:
            query_params = {
                'first_name': request.GET.get('first_name', '').strip(),
                'last_name': request.GET.get('last_name', '').strip(),
                'city': request.GET.get('city', '').strip(),
                'state': request.GET.get('state', '').strip(),
                'zip': request.GET.get('zip', '').strip(),
                'specialty': request.GET.get('specialty', '').strip()
            }

            page_number = request.GET.get('page', 1)
            sort_by = request.GET.get('sort_by', 'last_name')


            all_empty = all(value == '' for value in query_params.values())


            if all_empty:
                return render(request, 'search.html', {
                    'results': None,
                    'query': query_params,
                    'all_empty': True,
                    'sort_by': sort_by
                })

            sql = """
            SELECT 
                p.first_name,
                p.last_name,
                CONCAT(p.first_name, ' ', p.last_name) AS full_name,
                CONCAT_WS(', ', 
                    p.address_line1, 
                    NULLIF(p.address_line2, ''), 
                    p.city, 
                    p.state, 
                    p.zip
                ) AS address,
                COALESCE(STRING_AGG(DISTINCT t.classification, ', '), '') AS specialties,
                p.phone
            FROM providers p
            LEFT JOIN provider_taxonomy pt ON p.id = pt.provider_id
            LEFT JOIN taxonomy t ON pt.taxonomy_id = t.id
            WHERE 1=1
            """

            params = {}
            conditions = []

            for field, value in query_params.items():
                if value:
                    if field == 'state':
                        conditions.append(f"p.{field} = %({field})s")
                        params[field] = value.upper()
                    else:
                        conditions.append(f"p.{field} ILIKE %({field})s")
                        params[field] = f"%{value}%"

            if conditions:
                sql += " AND " + " AND ".join(conditions)

            sql += " GROUP BY p.id, p.first_name, p.last_name, p.address_line1, p.address_line2, p.city, p.state, p.zip, p.phone"

            if sort_by == 'specialty':
                sql += " ORDER BY specialties, p.last_name, p.first_name"
            elif sort_by == 'first_name':
                sql += " ORDER BY p.first_name, p.last_name"
            elif sort_by == 'last_name':
                sql += " ORDER BY p.last_name, p.first_name"
            elif sort_by == 'name':
                sql += " ORDER BY p.last_name, p.first_name"
            else:
                sql += " ORDER BY p.last_name, p.first_name"

            cursor.execute(sql, params)
            results = dictfetchall(cursor)

            paginator = Paginator(results, 20)
            page_obj = paginator.get_page(page_number)

            return render(request, 'search.html', {
                'results': page_obj,
                'query': query_params,
                'all_empty': False,
                'sort_by': sort_by
            })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)