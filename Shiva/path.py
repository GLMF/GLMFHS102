from dataclasses import dataclass

@dataclass
class Path:
    value : str

    def __truediv__(self, val : str) -> str:
        return self.value + '/' + val

if __name__ == '__main__':
    p = Path('/home/login')
    print(p / 'bin')
