def compare(old_times_or_file, new_times_or_file):
    pass


def show_times(times, style="csv", **kwargs):
    styled_times = convert_times(times, style, **kwargs)
    if style == "plot":
        styled_times.show()
    else:
        print(styled_times)
