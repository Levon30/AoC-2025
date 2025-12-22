from __future__ import annotations
from typing import Optional, Callable


test_input = '''
[.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}
[...#.] (0,2,3,4) (2,3) (0,4) (0,1,2) (1,2,3,4) {7,5,12,7,2}
[.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}
'''.strip()
test_solution = 7, 33

with open('input.txt') as f:
    puzzle_input = f.read().strip()


class State:
    def __init__(self, states: list[bool]):
        self.states = states

    def press(self, button: frozenset[int]) -> State:
        for i in button:
            self.states[i] = not self.states[i]
        return self

    def copy(self) -> State:
        return State(self.states.copy())


class Problem:
    def __init__(self, states: State, buttons: list[frozenset[int]], joltages: list[int]):
        self.states = states
        self.buttons = buttons
        self.joltages = joltages

    @classmethod
    def from_line(cls, line: str) -> Problem:
        a, *b, c = line.split(' ')
        states = [state == '.' for state in a[1:-1]]
        buttons = []
        for button in b:
            set_button = {int(i) for i in button[1:-1].split(',')}
            buttons.append(frozenset(set_button))
        joltages = [int(j) for j in c[1:-1].split(',')]
        return cls(State(states), buttons, joltages)

    def solve(self, part_b: bool) -> tuple[int, dict[frozenset[int], int]]:
        if not part_b:
            return self.solve_a(), {}

        def make_key(switch: bool):
            # Idea: We want buttons with many indices and also
            # buttons that can't be pressed many times.
            # It is unclear which one is more important, however
            # having small max_presses seems to work best.
            # Use the other one as a tie breaker.
            def _inner(button):
                max_presses = min([self.joltages[i] for i in button])
                indices = len(button)
                if switch:
                    max_presses, indices = indices, max_presses
                return max_presses + 0.5 / indices

            return _inner

        key = make_key(False)
        # self.buttons.sort(key=make_key(False))
        pressed_buttons = {b: 0 for b in self.buttons}
        solution, pressed_buttons = self.solve_b(0, sum(self.joltages) * 1000, 0, pressed_buttons, key)
        return solution, pressed_buttons

    def solve_a(self) -> Optional[int]:
        if all(self.states.states):
            return 0

        if len(self.buttons) == 0:
            return None

        button, rem_buttons = self.buttons[0], self.buttons[1:]
        a = Problem(self.states.copy().press(button), rem_buttons, [])
        a_solve = a.solve_a()

        b = Problem(self.states.copy(), rem_buttons, [])
        b_solve = b.solve_a()

        if a_solve is None:
            return b_solve
        if b_solve is None:
            return a_solve + 1
        return min(a_solve + 1, b_solve)

    def solve_b(self,
                presses: int,
                best_solution: int,
                depth: int,
                pressed_buttons: dict[frozenset[int], int],
                key: Callable
                ) -> tuple[Optional[int], dict[frozenset[int], int]]:

        sp = ' ' * depth
        log(sp)
        log(f'{sp}{self.joltages} {presses} {best_solution}')
        str_pr_but = [f'{tuple(x)}: {y}' for x, y in pressed_buttons.items()]
        str_pr_but = '; '.join(str_pr_but)
        log(f'{sp}{str_pr_but}')
        # log(f'{sp}{list(pressed_buttons.values())}')

        if presses >= best_solution or presses + max(self.joltages) >= best_solution:
            log(f'{sp}FAILED, no way to optimise best known solution')
            return None, {}

        if any(j < 0 for j in self.joltages):
            log(f'{sp}FAILED, negative joltage')
            return None, {}

        finished = set()
        unfinished = set()
        for i, j in enumerate(self.joltages):
            if j == 0:
                finished.add(i)
            else:
                unfinished.add(i)

        if not unfinished:
            return presses, pressed_buttons

        # We may now remove any button that contains any of the finished ids.
        buttons = [button for button in self.buttons if not finished.intersection(button)]
        buttons.sort(key=key)
        log(f'{sp}{[set(b) for b in self.buttons]} -> {[set(b) for b in buttons]}')

        if len(buttons) == 0:
            log(f'{sp}FAILED')
            return None, {}

        # If there's only 1 button left, we optimise the rest.
        if len(buttons) == 1:
            button = buttons.pop()
            s_joltages = set(self.joltages)
            if len(s_joltages) > 2 or button != unfinished:
                log(f'{sp}FAILED, last button does not solve problem')
                return None, {}
            new_presses = max(s_joltages)
            log(presses + new_presses)
            pressed_buttons[button] += new_presses
            return presses + new_presses, pressed_buttons

        # We now try to find buttons that are forced.
        # This dict stores the indices of all buttons containing i
        buttons_containing: dict[int, set[int]] = {}

        for i in unfinished:
            buttons_containing[i] = has_i = {b_id for b_id, b in enumerate(buttons) if i in b}
            if not has_i:
                # This means no button has i, but i still wants more juice
                log(f'{sp}FAILED, no more buttons left for {i}-th light')
                return None, {}

            if len(has_i) > 1:
                continue

            j = self.joltages[i]
            # We now simulate j many presses of this only button that contains i
            button = buttons[has_i.pop()]
            new_joltages = self.joltages.copy()
            for k in button:
                new_joltages[k] -= j
            # This will redo all these optimisations
            # It also terminates because `j` will be 0 next time (for this i)
            new_problem = Problem(self.states, [b for b in buttons if b is not button], new_joltages)
            pressed_buttons[button] += j
            log(f'{sp}> {button} is the only button left with {i}, simulate {j} many presses')
            return new_problem.solve_b(presses+j, best_solution, depth, pressed_buttons, key)

        for i, i_buttons in buttons_containing.items():
            for j, j_buttons in buttons_containing.items():
                if i == j:
                    continue
                if not i_buttons.issubset(j_buttons):
                    continue

                if self.joltages[i] > self.joltages[j]:
                    log(f'{sp}FAILED, every button containing {i} also contains {j}, but {i} has too high joltage left')
                    return None, {}

                diff = j_buttons.difference(i_buttons)
                if len(diff) != 1:
                    continue
                joltage_diff = self.joltages[j] - self.joltages[i]
                if joltage_diff == 0:
                    continue
                # Simulate `joltage_diff` many presses of that button
                j_button = buttons[diff.pop()]
                new_joltages = self.joltages.copy()
                for k in j_button:
                    new_joltages[k] -= joltage_diff
                new_problem = Problem(self.states, [b for b in buttons if b is not j_button], new_joltages)
                pressed_buttons[j_button] += joltage_diff
                log(f'{sp}> {j_button} is the only button left with {j} but not {i}, simulate {joltage_diff} many presses')
                return new_problem.solve_b(presses + joltage_diff, best_solution, depth, pressed_buttons, key)

        press_a_joltages = self.joltages.copy()
        for i in buttons[0]:
            press_a_joltages[i] -= 1
        a = Problem(self.states, buttons, press_a_joltages)
        a_buttons = pressed_buttons.copy()
        a_buttons[buttons[0]] += 1

        b = Problem(self.states, buttons[1:], self.joltages)
        b_buttons = pressed_buttons.copy()

        # Now solve both of them
        a_solve, a_buttons = a.solve_b(presses+1, best_solution, depth + 1, a_buttons, key)

        if a_solve is not None and a_solve < best_solution:
            pressed_buttons = a_buttons
            best_solution = a_solve

        b_solve, b_buttons = b.solve_b(presses, best_solution, depth + 1, b_buttons, key)

        if b_solve is not None and b_solve < best_solution:
            pressed_buttons = b_buttons
            best_solution = b_solve

        return best_solution, pressed_buttons


def solve(text: str, part_b: bool) -> int:

    problems = [Problem.from_line(line) for line in text.split('\n')]

    if not part_b:
        total = 0
        for p in problems:
            presses, _ = p.solve(False)
            total += presses
        return total

    # return problems[17].solve(True)
    # problems = [problems[86]]
    total = 0
    for _i, p in enumerate(problems):
        print(f'{_i} / {len(problems)}')
        # if _i == 165:
        #     total += 136
        # else:
        presses, pressed_buttons = p.solve(True)
        total += presses
        assert sum(pressed_buttons.values()) == presses
        print(presses)
    return total


def main():
    if test_solution[0] is not None:
        out = solve(test_input, False)
        assert out == test_solution[0], f'Got: {out}, Expected: {test_solution[0]}'
        print('Test A passed!')
    if test_solution[1] is not None:
        out = solve(test_input, True)
        # out = test_solution[1]
        assert out == test_solution[1], f'Got: {out}, Expected: {test_solution[1]}'
        print('Test B passed!')

    print('A:', solve(puzzle_input, False))
    print('B:', solve(puzzle_input, True))

if __name__ == '__main__':
    write_log = False

    if write_log:
        f = open('log.txt', 'w')

        def log(*texts, separator=' ', end='\n'):
            f.write(separator.join([str(text) for text in texts]) + end)
    else:
        f = None
        def log(*_, **__):
            pass

    main()

    if f is not None:
        f.close()

# 18232: Too low
# 18256: Too low
# 18273: Correct!
