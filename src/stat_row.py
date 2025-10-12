from pictex import Row, Text

EMOJI_FONT = "./fonts/NotoColorEmoji.ttf"

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

    def update_compose(self):
        """Update and compose the stat row with current values and appropriate colors"""
        stat = self.get_stat()
        stat_text = self.state_string(stat)
        stat_color = (
            "red"
            if self.is_critical(stat)
            else "orange" if self.is_warning(stat) else self.color
        )

        return Row(
            Text(self.icon).font_family(EMOJI_FONT),
            Text(self.label).color(self.color),
            Text(stat_text).color(stat_color),
        )