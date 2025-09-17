def get_url(*path_chunks) -> str:
    """
    Возвращает правильно сгенерированный урл для переданных частей пути
    """
    return '/'.join([chunk.strip('/') for chunk in path_chunks if chunk])
