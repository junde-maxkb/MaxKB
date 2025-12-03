from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.views import Request
import requests

from common.response import result
from common.auth import TokenAuth


class CNKIView(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['get'], detail=False)
    @swagger_auto_schema(
        operation_summary='Get CNKI document',
        operation_id='Get CNKI document',
        tags=['CNKI'],
    )
    def get(self, request: Request):

        query = request.GET.get('query')

        if not query:
            return result.error('查询文本异常')

        params = {
            'query': query,
            'limit': '10',
            'method': 'hybrid',
        }

        response = requests.get('http://172.16.99.54/weaviate/query/cnki_fulltext', params=params)
        if response.status_code != 200:
            return result.error('CNKI 文献知识库无法访问')
        json_data = response.json()

        if json_data['status'] != 'success':
            return result.error('CNKI 文献 Api 异常')

        return result.success(json_data['data'])


class CNKIAllFulltextView(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['get'], detail=False)
    @swagger_auto_schema(
        operation_summary='Get CNKI all fulltext document',
        operation_id='Get CNKI all fulltext document',
        tags=['CNKI'],
    )
    def get(self, request: Request):

        query = request.GET.get('query')

        if not query:
            return result.error('查询文本异常')

        params = {
            'query': query,
            'limit': '10',
        }

        response = requests.get('http://172.16.99.54/weaviate/query/cnki_all_fulltext', params=params)
        if response.status_code != 200:
            return result.error('CNKI Full 文献知识库无法访问')
        json_data = response.json()

        if json_data['status'] != 'success':
            return result.error('CNKI Full 文献 Api 异常')

        return result.success(json_data['data'])
