from __future__ import annotations
from typing import Optional


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

        self.mod_2_cache: dict[tuple[bool, ...], list[set[int]]] = {}

    def copy(self) -> Problem:
        obj = Problem(self.states.copy(), self.buttons.copy(), self.joltages.copy())
        obj.mod_2_cache = self.mod_2_cache
        return obj

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

    def solve(self, part_a: bool) -> int:
        if part_a:
            return self.solve_a()

        best_solution = sum(self.joltages)
        return self.solve_b(best_solution)

    def find_all_solutions_mod_2(self, disabled_buttons: Optional[set[int]] = None
                                 ) -> list[set[int]]:
        if disabled_buttons is None:
            disabled_buttons = set()

        key = tuple(self.states.states)
        if key not in self.mod_2_cache:
            # At first, my idea was to pass disabled_buttons to
            # the method that finds solutions mod 2, but that somewhat
            # interferes with caching. It turns out to be way faster
            # to disregard disabled_buttons when calculating solutions
            # and caching them. Instead we just filter the output of
            # this method (which is a minimal optimisation)
            self.mod_2_cache[key] = self._find_all_solutions_mod_2(set(), set())

        sols = self.mod_2_cache[key]
        return [sol for sol in sols if all(i not in sol for i in disabled_buttons)]

    def _find_all_solutions_mod_2(self,
                                  pressed: set[int],
                                  not_pressed: set[int]) -> list[set[int]]:
        buttons = []
        for i, b in enumerate(self.buttons):
            if i in pressed or i in not_pressed:
                continue
            buttons.append((i, b))

        if not buttons:
            if all(self.states.states):
                return [pressed]
            return []

        unfinished = [i for i, s in enumerate(self.states.states) if not s]

        # We now create a list of button ids containing
        # each of the unfinished indices

        buttons_containing: dict[int, set[int]] = {}
        for i in unfinished:
            buttons_containing[i] = {j for j, b in buttons if i in b}

            # If any unfinished index does not appear on a free
            # button, we may never solve this problem
            if not buttons_containing[i]:
                return []

        # Now if there is an unfinished index with only one button
        # to press, we do that immediately.
        for i, i_buttons in buttons_containing.items():
            if len(i_buttons) > 1:
                continue
            button_id = i_buttons.pop()
            i_button = self.buttons[button_id]
            self.states.press(i_button)
            pressed.add(button_id)

            return self._find_all_solutions_mod_2(pressed, not_pressed)

        # If no presses were forced we just try all remaining options.
        i, button = buttons.pop()

        # Now we copy the current problem and press the chosen button.
        new_problem = self.copy()
        new_problem.states.press(button)
        new_pressed = pressed.copy()
        new_pressed.add(i)
        solutions_a = new_problem._find_all_solutions_mod_2(new_pressed, not_pressed.copy())

        # Also try not pressing the button, return both solutions lists.
        not_pressed.add(i)
        return solutions_a + self._find_all_solutions_mod_2(pressed, not_pressed)

    def solve_a(self) -> int:
        solutions = self.find_all_solutions_mod_2()
        return min([len(solution) for solution in solutions])

    def solve_b(self, best_solution: int) -> Optional[int]:
        # Let A be the button matrix. We are then looking for
        # button presses p such that Ap = j.
        # Given such a solution p, consider this equation mod 2,
        # this yields a vector p0 (in {0, 1}^n),
        # which we can find efficiently.
        # Then p-p0 is a vector with even entries, so we divide by 2
        # which has now reduced the problem.

        # So here we do the following:
        # Get a list of all possible p0 solutions mod 2,
        # halve the joltage requirements and repeat.

        # We also keep track of the best solution we have found so far
        # to return early when exhausing the remaining options.

        if all(j == 0 for j in self.joltages):
            return 0
        if any(j < 0 for j in self.joltages):
            return None

        self.states = State([j % 2 == 0 for j in self.joltages])

        # We disable all buttons that cannot be legally pressed.
        # This would not be detected mod 2.
        disabled_buttons = set()
        for i, j in enumerate(self.joltages):
            if j != 0:
                continue
            for b_i, button in enumerate(self.buttons):
                if i in button:
                    disabled_buttons.add(b_i)

        sols_mod_2 = self.find_all_solutions_mod_2(disabled_buttons)

        for sol in sols_mod_2:
            presses = len(sol)
            if presses >= best_solution:
                continue

            new_problem = self.copy()
            for i in sol:
                button = self.buttons[i]
                for j in button:
                    new_problem.joltages[j] -= 1
            assert all(j%2 == 0 for j in new_problem.joltages)
            new_problem.joltages = [j // 2 for j in new_problem.joltages]

            # We simulate what the best solution would mean after
            # halving the problem.
            # The +1 makes it so that we round up.
            best_solution_sim = (best_solution - presses + 1) // 2
            new_presses = new_problem.solve_b(best_solution_sim)
            if new_presses is None:
                continue
            sol_presses = presses + 2 * new_presses
            best_solution = min(best_solution, sol_presses)

        return best_solution


def solve(text: str, part_a: bool) -> int:
    problems = [Problem.from_line(line) for line in text.split('\n')]
    return sum(p.solve(part_a) for p in problems)


def run(title: str, filename: str, part_a: bool, expected: int | None) -> None:
    with open(filename, 'r') as f:
        text = f.read().strip()

    got = solve(text, part_a)
    if expected is not None:
        assert got == expected, f'{title}; Got: {got}, Expected: {expected}'
        return
    print(f'{title}: {got}')


def main():
    import time

    test_solutions = 7, 33
    solutions = 475, 18273

    t_start = time.perf_counter()

    run('Test A', 'test_input.txt', True, test_solutions[0])
    run('Test B', 'test_input.txt', False, test_solutions[1])

    run('Problem A', 'input.txt', True, solutions[0])
    run('Problem B', 'input.txt', False, solutions[1])

    delay = time.perf_counter() - t_start
    print(f'All problems passed in {delay:.04f}s.')


if __name__ == '__main__':
    main()
