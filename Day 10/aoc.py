from __future__ import annotations

from typing import Optional

RECURSIVE_CACHE = True


class Problem:
    def __init__(self, states: set[int], buttons: list[frozenset[int]], joltages: list[int]):
        self.states = states
        self.buttons = buttons
        self.joltages = joltages

        self.mod_2_cache: dict[frozenset[int], list[set[int]]] = {}

    def press_states(self, button: frozenset[int]) -> None:
        self.states.symmetric_difference_update(button)

    def press_joltages(self, button: frozenset[int]) -> None:
        for i in button:
            self.joltages[i] -= 1

    def set_states(self) -> None:
        self.states = {i for i, j in enumerate(self.joltages) if j % 2 == 1}

    def copy(self) -> Problem:
        obj = Problem(self.states.copy(), self.buttons.copy(), self.joltages.copy())
        obj.mod_2_cache = self.mod_2_cache
        return obj

    @classmethod
    def from_line(cls, line: str) -> Problem:
        a, *b, c = line.split(' ')
        states = {i for i, c in enumerate(a[1:-1]) if c == '#'}
        buttons = []
        for button in b:
            set_button = {int(i) for i in button[1:-1].split(',')}
            buttons.append(frozenset(set_button))
        joltages = [int(j) for j in c[1:-1].split(',')]
        return cls(states, buttons, joltages)

    def solve(self, part_a: bool) -> int:
        if part_a:
            return self.solve_a()

        best_solution = sum(self.joltages)
        return self.solve_b(best_solution)

    def find_all_solutions_mod_2(self, disabled_buttons: Optional[set[int]] = None
                                 ) -> list[set[int]]:
        if disabled_buttons is None:
            disabled_buttons = set()

        key = frozenset(self.states)
        if self.states == {1, 2, 4, 5, 8}:
            pass

        if key not in self.mod_2_cache:
            # At first, my idea was to pass disabled_buttons to
            # the method that finds solutions mod 2, but that somewhat
            # interferes with caching. It turns out to be way faster
            # to disregard disabled_buttons when calculating solutions
            # and caching them. Instead we just filter the output of
            # this method (which is a minimal optimisation)
            new_sols = self._find_all_solutions_mod_2(set(), set())
            for sol in new_sols:
                if not self._validate_solution(set(key), sol):
                    print('Incorrect Cache')
                    print('Buttons:', [set(b) for b in self.buttons])
                    print('\t', key, sol)
                    pass
            self.mod_2_cache[key] = new_sols

        sols = self.mod_2_cache[key]
        return [sol for sol in sols if all(i not in sol for i in disabled_buttons)]

    def _find_all_solutions_mod_2(self,
                                  pressed: set[int],
                                  not_pressed: set[int]) -> list[set[int]]:
        buttons = []
        for j, b in enumerate(self.buttons):
            if j in pressed or j in not_pressed:
                continue
            buttons.append((j, b))

        # If there is a finished state with only one button that
        # contains this index, we never wish to press that button.
        # We iterate over all remaining buttons until no further
        # optimisation is possible.
        finished = [i for i in range(len(self.joltages)) if i not in self.states]
        while True:
            progress = False
            for i in finished:
                containing = {(j, b) for j, b in buttons if i in b}
                if len(containing) == 1:
                    progress = True
                    j, b = containing.pop()
                    buttons.remove((j, b))
                    not_pressed.add(j)
            if not progress:
                break

        if not buttons:
            if not self.states:
                return [pressed]
            return []

        # We now create a list of button ids containing the unfinished
        # machines. If for some _un_finished index, there is only
        # one button left, we have to press this button.

        buttons_containing: dict[int, set[int]] = {}
        for i in self.states:
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
            j = i_buttons.pop()
            i_button = self.buttons[j]
            self.press_states(i_button)
            pressed.add(j)

            return self._find_all_solutions_mod_2(pressed, not_pressed)

        # If no presses were forced we just try all remaining options.
        j, button = buttons.pop()

        # Now we copy the current problem and press the chosen button.
        new_problem = self.copy()
        new_problem.press_states(button)
        key = frozenset(new_problem.states)
        if key in self.mod_2_cache and RECURSIVE_CACHE:
            out = []
            for sol in self.mod_2_cache[key]:
                if sol.intersection(not_pressed):
                    continue
                if not pressed.issubset(sol):
                    continue
                out.append(sol.symmetric_difference({j}))

            return out

        new_pressed = pressed.copy()
        new_pressed.add(j)
        solutions_a = new_problem._find_all_solutions_mod_2(new_pressed, not_pressed.copy())

        if j == 9:
            pass

        # Also try not pressing the button, return both solutions lists.
        not_pressed.add(j)
        solutions_b = self._find_all_solutions_mod_2(pressed, not_pressed)
        return solutions_a + solutions_b

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

        # We disable all buttons that cannot be legally pressed.
        # This would not be detected mod 2.
        disabled_buttons = set()
        for i, j in enumerate(self.joltages):
            if j != 0:
                continue
            for b_i, button in enumerate(self.buttons):
                if i in button:
                    disabled_buttons.add(b_i)

        self.set_states()
        sols_mod_2 = self.find_all_solutions_mod_2(disabled_buttons)

        for sol in sols_mod_2:
            presses = len(sol)
            if presses >= best_solution:
                continue

            new_problem = self.copy()
            for i in sol:
                button = self.buttons[i]
                new_problem.press_joltages(button)
            assert all(j % 2 == 0 for j in new_problem.joltages)
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

    def _validate_solution(self, states: set[int], sol: set[int]) -> bool:
        states = states.copy()
        for i in sol:
            button = self.buttons[i]
            states.symmetric_difference_update(button)
        return not states

def solve(text: str, part_a: bool) -> int:
    problems = [Problem.from_line(line) for line in text.split('\n')]
    total = 0
    for problem in problems:
        presses = problem.solve(part_a)
        # print(presses)
        total += presses
    return total
    # return sum(p.solve(part_a) for p in problems)


def main2():
    with open('test_input.txt') as f:
        text = f.read()
    print(solve(text, True))

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
