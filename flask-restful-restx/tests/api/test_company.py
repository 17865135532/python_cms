from app.dao.mysql import db
from app.models import Company
from tests import helpers, constants
from app.utils import errors
import pytest


class TestCompanies:
    def setup_method(self):
        company = db.session.query(Company).filter(Company.tax_number == 'XXXXXXXXXXXXXXXXX2').first()
        if company:
            company.delete()

    def teardown_method(self):
        if getattr(self, 'company_id', None) is not None:
            company = db.session.query(Company).filter(Company.company_id == self.company_id).first()
            company.delete()

    def check_company(self, data, action='create', registration_number='', tax_authority_code=''):
        assert data.get("company_id") == self.company_id
        assert data.get("company_name") == '测试专用公司2'
        assert data.get("tax_number") == 'XXXXXXXXXXXXXXXXX2'
        if action == 'create':
            assert data.get("province") == '北京市'
            assert data.get("head_office") == '北京市'
            assert data.get("taxpayer_identification") == '一般纳税人'
            assert data.get("login_way") == 'CA'
            assert data.get("login_account") == 'test2'
            assert data.get("login_password") == 'Abc123'
            assert data.get("natural_person_password") == 'Efg09876'
            assert data.get("company_state") == 'active'
            assert data.get("registration_number") == registration_number
            assert data.get("tax_authority_code") == tax_authority_code

        if action == 'update':
            assert data.get("province") == '天津市'
            assert data.get("head_office") == '天津市'
            assert data.get("taxpayer_identification") == '小规模纳税人'
            assert data.get("login_way") == 'id_card'
            assert data.get("login_account") == 'test2'
            assert data.get("login_password") == '3333333'
            assert data.get("natural_person_name") == '李四'
            assert data.get("natural_person_ID") == '11111111111111111x'
            assert data.get("natural_person_password") == 'Efg09876'
            assert data.get("taxpayer_name") == '王五'
            assert data.get("taxpayer_ID") == '22222222222222222'
            assert data.get("taxpayer_telephone") == '3333333'
            assert data.get("registration_number") == registration_number
            assert data.get("tax_authority_code") == tax_authority_code

    def check_ad_company(self, data, action='create', registration_number='', tax_authority_code=''):
        assert data.get("company_id") == self.company_id
        assert data.get("company_name") == '测试专用公司2'
        assert data.get("tax_number") == 'XXXXXXXXXXXXXXXXX2'

        if action == 'create':
            assert data.get("province") == '天津市'
            assert data.get("head_office") == '天津市'
            assert data.get("taxpayer_identification") == '一般纳税人'
            assert data.get("login_way") == 'CA'
            assert data.get("login_account") == 'test2'
            assert data.get("login_password") == 'Abc456'
            assert data.get("company_state") == 'active'
            assert data.get("registration_number") == registration_number
            assert data.get("tax_authority_code") == tax_authority_code
        elif action == 'update':
            assert data.get("province") == '北京市'
            assert data.get("head_office") == '北京市'
            assert data.get("taxpayer_identification") == '小规模纳税人'
            assert data.get("login_way") == 'id_card'
            assert data.get("login_account") == 'test2'
            assert data.get("login_password") == '3333333'
            assert data.get("natural_person_name") == '李四'
            assert data.get("natural_person_ID") == '11111111111111111x'
            assert data.get("natural_person_password") == 'Efg09876'
            assert data.get("taxpayer_ID") == '22222222222222222'
            assert data.get("taxpayer_telephone") == '3333333'
            assert data.get("company_state") == 'active'
            assert data.get("registration_number") == registration_number
            assert data.get("tax_authority_code") == tax_authority_code

    def test_workflow(self, client):
        # 创建公司
        path = '/api/v1/companies'
        raw_body = {
            'company_name': '测试专用公司2',
            'tax_number': 'XXXXXXXXXXXXXXXXX2',
            'taxpayer_identification_code': '2000010001',
            'login_way_code': 1,
            'login_account': 'test2',
            'login_password': 'Abc123',
            'province_code': '11',
            'head_office_code': '11',
            'valid_start_date': '2000-01-01T00:00:00Z',
            'valid_end_date': '2999-01-01T00:00:00Z',
            'natural_person_password': 'Efg09876',
            'registration_number': "10113501000034521900",
            'tax_authority_code': "13501030000"
        }
        headers, body = helpers.format_headers_and_body(raw_body)
        rv = client.post(path, json=body, headers=headers)
        res = helpers.validate_resp(rv, path=path, method='post', data=body)
        data = res.get('data')
        assert data, res
        self.company_id = data.get("company_id")
        assert isinstance(self.company_id, int), data
        self.check_company(data, registration_number='10113501000034521900',
                           tax_authority_code='13501030000')

        # 修改公司信息
        path = f'/api/v1/companies/{self.company_id}'
        raw_body = {
            'natural_person_name': '李四',
            'natural_person_ID': '11111111111111111x',
            'natural_person_password': 'Efg09876',
            'taxpayer_name': '王五',
            'taxpayer_ID': '22222222222222222',
            'taxpayer_telephone': '3333333',
            'login_password': '3333333',
            'province_code': '12',
            'head_office_code': '12',
            'taxpayer_identification_code': '2000010002',
            'login_way_code': 4
        }
        headers, body = helpers.format_headers_and_body(raw_body)
        rv = client.post(path, json=body, headers=headers)
        res = helpers.validate_resp(rv, path=path, method='post', data=body)
        data = res.get('data')
        assert data, res
        self.check_company(data, action='update', registration_number='10113501000034521900',
                           tax_authority_code='13501030000')

        # 批量查询公司信息
        params = {
            'create_date_start': constants.YESTERDAY.strftime('%Y-%m-%d'),
            'create_date_end': constants.TOMORROW.strftime('%Y-%m-%d'),
            'page': 1,
            'per_page': 100000000,
            'company_name': '测试',
            'tax_number': 'XXX2',
            'province': '津',
            'user_id': 1,
            'company_state': 'active'
        }
        headers1, _ = helpers.format_headers_and_body()
        headers2, _ = helpers.format_headers_and_body(params=params)
        path1 = f'/api/v1/companies'
        path2 = f'/api/v1/companies' + '?' + '&'.join([f'{k}={v}' for k, v in params.items()])
        for path, _headers in [(path1, headers1), (path2, headers2)]:
            rv = client.get(path, headers=_headers)
            res = helpers.validate_resp(rv, path=path, method='get')
            data = res.get('data')
            assert data, res
            companies = data.get('companies')
            assert isinstance(companies, list), data
            for company in companies:
                if company.get('company_id') == self.company_id:
                    self.check_company(
                        company, action='update',
                        registration_number='10113501000034521900',
                        tax_authority_code='13501030000')
                    break
            else:
                assert 0, data

        # 查询公司信息
        headers, _ = helpers.format_headers_and_body()
        path = f'/api/v1/companies/{self.company_id}'
        rv = client.get(path, headers=headers)
        res = helpers.validate_resp(rv, path=path, method='get')
        data = res.get('data')
        assert data, res
        assert data.get('company_id') == self.company_id, data
        self.check_company(company, action='update',
                        registration_number='10113501000034521900',
                        tax_authority_code='13501030000')

    def test_ad_workflow(self, client):
        # 创建公司
        path = '/api/v1/ad/companies'
        raw_body = {
            'company_name': '测试专用公司2',
            'tax_number': 'XXXXXXXXXXXXXXXXX2',
            'taxpayer_identification_code': '2000010001',
            'login_way_code': 1,
            'login_account': 'test2',
            'login_password': 'Abc456',
            'province_code': '12',
            'head_office_code': '12',
            'valid_start_date': '2000-01-01T00:00:00Z',
            'valid_end_date': '2999-01-01T00:00:00Z',
            "user_id": 1,
            'registration_number': "10113501000034521900",
            'tax_authority_code': "13501030000"
        }
        headers, body = helpers.format_headers_and_body(raw_body)
        rv = client.post(path, json=body, headers=headers)
        res = helpers.validate_resp(rv, path=path, method='post', data=body)
        data = res.get('data')
        assert data, res
        self.company_id = data.get("company_id")
        assert isinstance(self.company_id, int), data
        self.check_ad_company(data,
                        registration_number='10113501000034521900',
                        tax_authority_code='13501030000')

        # 修改公司信息
        path = f'/api/v1/ad/companies/{self.company_id}'
        raw_body = {
            'natural_person_name': '李四',
            'natural_person_ID': '11111111111111111x',
            'natural_person_password': 'Efg09876',
            'taxpayer_name': '王五',
            'taxpayer_ID': '22222222222222222',
            'taxpayer_telephone': '3333333',
            'login_password': '3333333',
            'province_code': '11',
            'head_office_code': '11',
            'taxpayer_identification_code': '2000010002',
            'user_id': 1,
            'login_way_code': 4
        }
        headers, body = helpers.format_headers_and_body(raw_body)
        rv = client.post(path, json=body, headers=headers)
        res = helpers.validate_resp(rv, path=path, method='post', data=body)
        data = res.get('data')
        assert data, res
        self.check_ad_company(data, action='update',
                        registration_number='10113501000034521900',
                        tax_authority_code='13501030000')

        # 批量查询公司信息
        params = {
            'create_date_start': constants.YESTERDAY.strftime('%Y-%m-%d'),
            'create_date_end': constants.TOMORROW.strftime('%Y-%m-%d'),
            'page': 1,
            'per_page': 1000000,
            'company_name': '测试',
            'tax_number': 'XXX2',
            'province': '京',
            'user_id': 1
        }
        headers1, _ = helpers.format_headers_and_body()
        headers2, _ = helpers.format_headers_and_body(params=params)
        path1 = f'/api/v1/ad/companies'
        path2 = f'/api/v1/ad/companies' + '?' + '&'.join([f'{k}={v}' for k, v in params.items()])
        for path, _headers in [(path1, headers1), (path2, headers2)]:
            rv = client.get(path, headers=_headers)
            res = helpers.validate_resp(rv, path=path, method='get')
            data = res.get('data')
            assert data, res
            companies = data.get('companies')
            assert isinstance(companies, list), data
            for company in companies:
                if company.get('company_id') == self.company_id:
                    self.check_ad_company(
                        company, action='update',
                        registration_number='10113501000034521900',
                        tax_authority_code='13501030000')
                    break
            else:
                assert 0, data

        # 查询公司信息
        headers, _ = helpers.format_headers_and_body()
        path = f'/api/v1/ad/companies/{self.company_id}'
        rv = client.get(path, headers=headers)
        res = helpers.validate_resp(rv, path=path, method='get')
        data = res.get('data')
        assert data, res
        assert data.get('company_id') == self.company_id, data
        self.check_ad_company(data, action='update',
                        registration_number='10113501000034521900',
                        tax_authority_code='13501030000')

    def test_creation_404(self, client):
        # 创建公司
        raw_body = {
            'company_name': '测试专用公司2',
            'tax_number': 'XXXXXXXXXXXXXXXXX2',
            'taxpayer_identification_code': 2000010001,
            'login_way_code': 1,
            'login_account': 'test2',
            'login_password': 'Abc123456',
            'province_code': '11',
            'head_office_code': '11',
            'valid_start_date': 'a',
            'valid_end_date': 'b'
        }
        path = '/api/v1/companies'
        headers, body = helpers.format_headers_and_body(raw_body)
        rv = client.post(path, json=body, headers=headers)
        helpers.validate_resp(rv, expected_return_code=errors.ErrorCode.DataParamError.value, path=path, method='get')
