class progressBar:
    """
    A class for generating progress bars with customizable styles.

    Attributes:
        total (int): The total value representing the completion of the progress.
        current (int): The current value indicating the progress.
        size (int): The size of the progress bar.
        line (str): The character representing the filled portion of the progress bar.
        slider (str): The character representing the slider or indicator of the progress.

    Methods:
        splitBar(total, current, size=15, line="▬", slider="🔘"):
            Generates a progress bar with two different styles.
        filledBar(total, current, size=15, line="⬛", slider="⬜"):
            Generates a progress bar with filled style.
    """
    
    def splitBar(total, current, size=15, line="▬", slider="🔘"):
        """
        Generate a split-style progress bar.

        Args:
            total (int): The total value representing the completion of the progress.
            current (int): The current value indicating the progress.
            size (int, optional): The size of the progress bar. Defaults to 15.
            line (str, optional): The character representing the filled portion of the progress bar. Defaults to "▬".
            slider (str, optional): The character representing the slider or indicator of the progress. Defaults to "🔘".

        Returns:
            list: A list containing the progress bar string and the percentage completed.
        """
        # If current progress exceeds total
        if current > total:
            # Fill the entire bar
            bar = line * size
            # Calculate percentage
            percentage = (current / total) * 100

            return [bar, percentage]
        else:
            # Calculate percentage of progress
            percentage = current / total
            # Calculate filled and empty progress
            progress = round(size * percentage)
            emptyProgress = size - progress

            # Construct progress bar string
            progressText = (line * progress)[:-1] + slider
            emptyProgressText = line * emptyProgress
            bar = progressText + emptyProgressText

            # Calculate percentage
            calculated = percentage * 100

            return [bar, calculated]

    def filledBar(total, current, size=15, line="⬛", slider="⬜"):
        """
        Generate a filled-style progress bar.

        Args:
            total (int): The total value representing the completion of the progress.
            current (int): The current value indicating the progress.
            size (int, optional): The size of the progress bar. Defaults to 15.
            line (str, optional): The character representing the filled portion of the progress bar. Defaults to "⬛".
            slider (str, optional): The character representing the slider or indicator of the progress. Defaults to "⬜".

        Returns:
            list: A list containing the progress bar string and the percentage completed.
        """
        # If current progress exceeds total
        if current > total:
            # Fill the entire bar
            bar = slider * size
            # Calculate percentage
            percentage = (current / total) * 100
            return [bar, percentage]
        else:
            # Calculate percentage of progress
            percentage = current / total
            # Calculate filled and empty progress
            progress = round(size * percentage)
            emptyProgress = size - progress

            # Construct progress bar string
            progressText = slider * progress
            emptyProgressText = line * emptyProgress

            bar = progressText + emptyProgressText
            # Calculate percentage
            calculated = percentage * 100
            return [bar, calculated]
