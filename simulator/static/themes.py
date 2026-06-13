# static/themes.py
class Temas:
    @staticmethod
    def tema_oscuro():
        return """
        <style>
            body { background: #1a1a1a; color: #fff; }
            .stat-card { background: #2d2d2d; color: #fff; }
            .stat-value { color: #fff; }
            select, input { background: #3d3d3d; color: #fff; border-color: #555; }
        </style>
        """
    
    @staticmethod
    def tema_claro():
        return """
        <style>
            body { background: #f5f5f5; color: #333; }
            .stat-card { background: white; color: #333; }
        </style>
        """
    
    @staticmethod
    def tema_cyberpunk():
        return """
        <style>
            body { background: #0a0a0a; color: #0ff; font-family: 'Courier New', monospace; }
            .stat-card { background: #1a1a1a; border: 2px solid #0ff; box-shadow: 0 0 20px #0ff; }
            .stat-value { color: #f0f; text-shadow: 0 0 10px #f0f; }
            button { background: #0ff; color: #000; font-weight: bold; }
            button:hover { background: #f0f; }
        </style>
        """