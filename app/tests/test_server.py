def test_default_log_level(app):
    assert app.logger.level == 20


def test_env_log_level(app_debug):
    assert app_debug.logger.level == 10
