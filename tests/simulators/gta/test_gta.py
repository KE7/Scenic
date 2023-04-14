
import matplotlib.pyplot as plt
import pytest

from scenic.simulators.gta.interface import GTA
from tests.utils import compileScenic, sampleScene, pickle_test, tryPickling

# Skip tests if Pillow or OpenCV not installed
pytest.importorskip("PIL")
pytest.importorskip("cv2")

def test_basic(loadLocalScenario):
    scenario = loadLocalScenario('basic.scenic')
    scene = sampleScene(scenario, maxIterations=1000)
    GTA.Config(scene)

@pytest.mark.graphical
def test_show_2d(loadLocalScenario):
    scenario = loadLocalScenario('basic.scenic')
    scene = sampleScene(scenario, maxIterations=1000)
    scene.show_2d(block=False)
    plt.close()
    scene.show_2d(zoom=1, block=False)
    plt.close()

def test_bumper_to_bumper(loadLocalScenario):
    scenario = loadLocalScenario('bumperToBumper.scenic')
    scene = sampleScene(scenario, maxIterations=1000)
    GTA.Config(scene)

def test_make_map(request, tmp_path):
    from scenic.simulators.gta.interface import Map
    m = Map(request.path.parent / 'small.png',
        Ax=1, Ay=-1, Bx=-700, By=500)
    outpath = tmp_path / 'gta_map.npz'
    m.dumpToFile(outpath)
    outpath.unlink()

def test_mutate():
    scenario = compileScenic(
        'from scenic.simulators.gta.map import setLocalMap\n'
        f'setLocalMap("{__file__}", "map.npz")\n'
        'from scenic.simulators.gta.model import *\n'
        'ego = new EgoCar with color Color(0, 0, 1)\n'
        'mutate'
    )
    scene, _ = scenario.generate(maxIterations=50)
    assert tuple(scene.egoObject.color) != (0, 0, 1)

@pickle_test
def test_pickle(loadLocalScenario):
    scenario = loadLocalScenario('basic.scenic')
    unpickled = tryPickling(scenario)
    scene = sampleScene(unpickled, maxIterations=1000)
    tryPickling(scene)
