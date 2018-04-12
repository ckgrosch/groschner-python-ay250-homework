from hw_8 import app

test_app = app.test_client()

def test_index():
    response = test_app.get('/')
    assert 'BUTTS' in response.data.decode('utf-8')
