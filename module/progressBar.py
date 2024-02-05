class progressBar:
    def splitBar(total, current, size=15, line="▬", slider="🔘"):
        if current > total:
            bar = line * size
            percentage = (current / total) * 100

            return [bar, percentage]
        else:
            percentage = current / total
            progress = round(size * percentage)
            emptyProgress = size - progress

            progressText = (line * progress)[:-1] + slider
            emptyProgressText = line * emptyProgress
            bar = progressText + emptyProgressText

            calculated = percentage * 100

            return [bar, calculated]

    def filledBar(total, current, size=15, line="⬛", slider="⬜"):
        if current > total:
            bar = slider * size
            percentage = (current / total) * 100
            return [bar, percentage]
        else:
            percentage = current / total
            progress = round(size * percentage)
            emptyProgress = size - progress

            progressText = slider * progress
            emptyProgressText = line * emptyProgress

            bar = progressText + emptyProgressText
            calculated = percentage * 100
            return [bar, calculated]
