def split_string(input_string, max_length=20):
    """
    Splits a string into smaller strings with a maximum length.

    Args:
        input_string (str): The input string to be split.
        max_length (int, optional): The maximum length of each smaller string. Defaults to 20.

    Returns:
        list: A list of smaller strings.
    """
    # Return a list containing the input string if its length is less than or equal to max_length.
    if len(input_string) <= max_length:
        return [input_string]

    # Use list comprehension to split the input string into smaller strings of length max_length.
    return [input_string[i:i + max_length] for i in range(0, len(input_string), max_length)]
