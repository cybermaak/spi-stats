class StatRow:
    """A class representing a single statistic row with icon, label, and dynamic value"""
    def __init__(
        self, icon, label, color, get_stat, state_string, is_warning, is_critical
    ):
        self.icon = icon
        self.label = label
        self.color = color
        self.get_stat = get_stat
        self.state_string = state_string
        self.is_warning = is_warning
        self.is_critical = is_critical

    def get_render_data(self):
        """Get current stat data for direct PIL rendering"""
        stat = self.get_stat()
        stat_text = self.state_string(stat)
        stat_color = (
            "red"
            if self.is_critical(stat)
            else "orange" if self.is_warning(stat) else self.color
        )
        
        return {
            'icon': self.icon,
            'icon_color': self.color,
            'value': stat_text,
            'value_color': stat_color
        }

    def update_compose(self):
        """Legacy method for compatibility - returns render data"""
        return self.get_render_data()
