import json

from grapejuice_common.graphics_detect.graphics_capabilities import GraphicsCapabilities
from grapejuice_common.graphics_detect.lspci import LSPci


def main():
    pci = LSPci()
    cap = GraphicsCapabilities(pci)
    as_json = json.dumps({
        "kernel_drivers": cap.all_kernel_drivers,
        "hybrid_graphics": cap.hybrid_graphics,
        "graphics_vendors": list(map(lambda e: e.name, cap.graphics_vendors))
    }, indent=2)

    print(as_json)


if __name__ == '__main__':
    main()
