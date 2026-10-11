"""Direct-call activation observations in disposable engineering fixtures."""
import sys

import nox


@nox.session(python=False, tags=["full"])
def playide_activation(session: nox.Session) -> None:
    """Observe real services, retained source identity and behavioral negative controls; never stamp source."""
    session.run(sys.executable, "-m", "verification.selfdogfood", "--out", "reports/activation-selfdogfood.json")
