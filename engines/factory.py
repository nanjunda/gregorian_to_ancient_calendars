from engines.panchanga.engine import PanchangaEngine

class EngineFactory:
    """
    Registry of available ancient calendar engines.
    """
    _engines = {
        "panchanga": PanchangaEngine(),
        # Future slots:
        # "mayan": MayanEngine(),
        # "chinese": ChineseEngine()
    }

    @classmethod
    def get_engine(cls, engine_name):
        engine = cls._engines.get(engine_name.lower())
        if not engine:
            raise ValueError(f"Unknown calendar engine: {engine_name}")
        return engine

    @classmethod
    def list_engines(cls):
        return list(cls._engines.keys())
