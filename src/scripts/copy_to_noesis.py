import os
import shutil


def copy_script():
    noesis_path = os.environ['NOESIS_PATH']
    script_name = "ea_graph_man_noesis_script.py"
    output_path = os.path.join(noesis_path, script_name)
    shutil.copy2(f'./{script_name}', output_path)
    print("Script copied successfully!")


if __name__ == "__main__":
    copy_script()
