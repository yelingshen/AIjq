from ai.scanner.dispatcher import ScannerDispatcher
__all__ = ['ScannerDispatcher']

def get_dispatcher(*args, **kwargs):
    return ScannerDispatcher(*args, **kwargs)

