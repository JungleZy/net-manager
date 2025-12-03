import os
import tempfile
import json
from tornado.testing import AsyncHTTPTestCase
from src.network.api.api_server import APIServer
from src.database import DatabaseManager


class TestAPIServer(AsyncHTTPTestCase):
    def setUp(self):
        self._tmp_db = tempfile.NamedTemporaryFile(delete=False)
        self._tmp_db.close()
        super().setUp()

    def tearDown(self):
        try:
            os.unlink(self._tmp_db.name)
        except Exception:
            pass
        super().tearDown()

    def get_app(self):
        dbm = DatabaseManager(db_path=self._tmp_db.name)
        api = APIServer(db_manager=dbm)
        return api.app

    def test_health(self):
        resp = self.fetch('/health')
        assert resp.code == 200
        data = json.loads(resp.body.decode('utf-8'))
        assert data.get('status') == 'healthy'
        assert data.get('service')

    def test_healthz(self):
        resp = self.fetch('/healthz')
        assert resp.code == 200
        data = json.loads(resp.body.decode('utf-8'))
        assert data.get('status') == 'healthy'

    def test_metrics(self):
        resp = self.fetch('/api/metrics')
        assert resp.code == 200
        data = json.loads(resp.body.decode('utf-8'))
        assert data.get('status') == 'success'
        metrics = data.get('data', {})
        assert 'db_health' in metrics
        assert 'tcp_client_count' in metrics
        assert 'message_count' in metrics
