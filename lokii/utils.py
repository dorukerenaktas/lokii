def print_start(curr: int, total: int) -> None:
    completed = curr / total

    print('|{}|'.format(
        ''.join([
            '#' if i / 100 <= completed else '_'
            for i in range(100)
        ])
    ), end='\r', flush=True)


def print_process(curr: int, total: int) -> None:
    completed = curr / total

    print('|{}|'.format(
        ''.join([
            '#' if i / 100 <= completed else '_'
            for i in range(100)
        ])
    ), end='\r', flush=True)