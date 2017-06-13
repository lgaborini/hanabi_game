# Hanabi simulation

Simulate stochastic Hanabi games in order to extract endgame statistics.

- Output is collected to .csv.   
- Moves are logged into `hanabi.log`, scores into `scores.csv`.
- Perfect plays are assumed (e.g. hints are useless, play the best card if possible).   
- Hanabi game events are dispatched as custom `Exceptions`.
- The game status can be displayed in color using ANSI escape codes in a supported terminal:   
  e.g. `tail -f hanabi.log` in `bash`
