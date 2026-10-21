# RB Lifeline

**RB Lifeline** helps an offensive coach answer one question: when pressure reaches my quarterback (QB), is my running back (RB) there as an outlet? On every pass play, we find the first frame where a defender gets within 2 yards of the QB, then check from tracking data whether the RB is running a route, open (no defender within 2.5 yards), within 15 yards of the QB, no more than 1 yard behind the line of scrimmage, and turned toward the QB (QB within 120° of the RB's body orientation). The coach dashboard replays each pressured play of a game in 2D, shows frame by frame whether the RB is available, and summarizes how often each RB gives the QB an outlet, so the staff knows which plays and protections to review on film. Each RB also gets a Lifeline score: how often he is available under pressure, multiplied by how reliably he catches the ball. Beyond coaching, the same score gives scouts a way to compare third-down RBs and gives broadcasters a ready-made "Best safety valves" ranking.

## How to run

After cloning, run `./run` (requires Python 3.11+, Git and internet on first setup).
It creates `.venv`, installs dependencies and launches the starter dashboard.
Verify: `./prepare_environnement --check --no-skills` and `./test_env --no-skills`.
See [SETUP.md](SETUP.md) for dependencies, notebooks and optional AWS support.

## Development

RB Lifeline development: [specifications](spec/README.md), [architecture and contracts](adr/README.md), [implementation split](adr/IMPLEMENTATION.md).
