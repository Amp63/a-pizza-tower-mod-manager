import platform
import os
import subprocess
import shutil
import configparser
from tkinter import filedialog

HOME_PATH = os.path.expanduser('~')
ROOT_PATH = os.path.abspath('/')
PIZZATOWER_PATH = None


def find_pizza_tower_path() -> str | None:
    if platform.system() == 'Windows':
        pt_path = f'{ROOT_PATH}/Program Files (x86)/Steam/steamapps/common/Pizza Tower'
    elif platform.system() == 'Linux':
        pt_path = f'{HOME_PATH}/.steam/root/steamapps/common/Pizza Tower'
    
    if os.path.exists(pt_path):
        return pt_path
    return None


def apply_patch(patch_data_path: str) -> bool:
    file_name = os.path.basename(patch_data_path)
    if file_name != 'data.win':
        return False
    
    if not os.path.exists(patch_data_path):
        return False

    data_path = f'{PIZZATOWER_PATH}/data.win'
    os.remove(data_path)
    shutil.copy(patch_data_path, data_path)
    return True


def new_patch_cli():
    xdelta_path = filedialog.askopenfilename(title='Select an XDelta file.', defaultextension='.xdelta', filetypes=[('Patch Files', '*.xdelta')])
    if not xdelta_path:
        print('Please select a file.')
        return
    ext = os.path.splitext(xdelta_path)[1]
    if ext != '.xdelta':
        print('Please select an xdelta file.')
        return
    
    patch_name = os.path.splitext(os.path.basename(xdelta_path))[0]
    os.makedirs(f'patches/{patch_name}')
    dest_path = f'patches/{patch_name}/data.win'
    
    os.system(f'xdelta3 -d -s "vanilla/data.win" "{xdelta_path}" "{dest_path}"')

    print(f'Created patch {patch_name} successfully!')
    apply_patch_response = input(f'Would you like to apply the patch? [Y/n] ').strip()
    if apply_patch_response.lower() == 'y' or apply_patch_response == '':
        applied = apply_patch(dest_path)
        if applied:
            print('Patch applied successfully!')
        else:
            print('Please input a data.win file.')


def apply_patch_cli():
    dirs = os.listdir('patches')

    print('Choose a patch to apply:')
    
    for i, dir_name in enumerate(dirs):
        print(f'  [{i+1}] {dir_name}')
    
    response = input('> ')
    if not response.isnumeric():
        return
    
    patch_index = int(response)-1
    if patch_index < 0 or patch_index >= len(dirs):
        return
    
    patch_name = dirs[patch_index]
    data_path = f'patches/{patch_name}/data.win'
    if os.path.exists(data_path):
        apply_patch(data_path)
        print(f'Patch {patch_name} applied successfully!')
    else:
        print(f'Could not find data.win file for {patch_name}')


def is_xdelta3_installed() -> bool:
    try:
        subprocess.run(['xdelta3', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True
    except FileNotFoundError:
        return False


def initial_setup() -> int:
    pt_path = find_pizza_tower_path()
    if pt_path is None:
        print('Could not find Pizza Tower installation. Please select your "Pizza Tower" Steam folder.')
        pt_path = filedialog.askdirectory()
        if not pt_path:
            return 1
    
    if not is_xdelta3_installed():
        print('Please install xdelta3 before continuing.')
        return 2

    
    print('Before we get started, be sure that your game is currently unmodified. If it is modified, just verify the integrity of your game files before continuing.\n')
    print("[1] I currently have an unmodified version of the game.")
    print("[0] Cancel")
    response = input('> ').strip()
    if response != '1':
        return 3
    
    if not os.path.exists(f'{pt_path}/data.win'):
        print('Could not find data.win file in Pizza Tower directory.')
        return 4
    
    os.makedirs(f'vanilla')
    os.makedirs(f'patches')
    config = configparser.ConfigParser()
    config['pizzatower'] = {'path': pt_path}
    with open(f'ptmm.cfg', 'w') as f:
        config.write(f)
    shutil.copy(f'{pt_path}/data.win', f'vanilla/data.win')
    return 0
    


def main():
    if not os.path.exists('ptmm.cfg'):
        if initial_setup() != 0:
            return
    
    config = configparser.ConfigParser()
    config.read('ptmm.cfg')
    global PIZZATOWER_PATH
    PIZZATOWER_PATH = config['pizzatower']['path']

    print('Welcome to A Pizza Tower Mod Manager!\n')

    while True:  
        print('  [1] Create New Patch')
        print('  [2] Apply Patch')
        print('  [3] Revert to Vanilla')
        print('  [0] Quit')
        print()

        response = input('> ').strip()
        if response == '0':
            break
        elif response == '1':
            new_patch_cli()
        elif response == '2':
            apply_patch_cli()
        elif response == '3':
            revert = input('Are you sure you want to revert to vanilla? [Y/n] ')
            if revert.lower() == 'y' or revert == '':
                apply_patch('vanilla/data.win')
                print('Your game has been reverted to vanilla.')
        
        print()
    
    print('See ya later!')

if __name__ == '__main__':
    main() 