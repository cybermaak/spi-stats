class StatRow:
    """A class representing a single statistic row with icon, label, and dynamic value"""
    def __init__(
        self, icon, label, color, get_stat, state_string, is_warning, is_critical,
        get_percentage=None, visual_label=None
    ):
        self.icon = icon
        self.label = label
        self.color = color
        self.get_stat = get_stat
        self.state_string = state_string
        self.is_warning = is_warning
        self.is_critical = is_critical
        self.get_percentage = get_percentage  # Function to extract percentage value
        self.visual_label = visual_label  # Custom label function for visual mode

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

    def get_visual_data(self):
        """Get data for visual mode rendering with progress bars"""
        stat = self.get_stat()
        
        # Determine percentage value
        if self.get_percentage:
            percentage = self.get_percentage(stat)
        else:
            percentage = 0  # Default for non-percentage stats like IP
        
        # Determine label text
        if self.visual_label:
            label_text = self.visual_label(stat)
        else:
            label_text = self.state_string(stat)
        
        # Determine color based on thresholds
        stat_color = (
            "red"
            if self.is_critical(stat)
            else "orange" if self.is_warning(stat) else self.color
        )
        
        return {
            'icon': self.icon,
            'icon_color': self.color,
            'label': label_text,
            'percentage': percentage,
            'bar_color': stat_color,
            'has_bar': self.get_percentage is not None  # Whether to show a progress bar
        }

    def update_compose(self):
        """Legacy method for compatibility - returns render data"""
        return self.get_render_data()
