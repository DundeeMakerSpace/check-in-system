#! /usr/bin/doit -f

from doit.action import CmdAction

def task_libnfc_clone():
    """Clones libnfc source code from git submodule"""
    return {
        'actions': [
            CmdAction('git submodule init'),
            CmdAction('git submodule update'),
        ],
        'file_dep': ['.gitmodules',],
        'targets': ['libnfc/configure.ac',],
        'verbosity': 2,
    }

def task_libnfc_autoreconf():
    """Update libnfc's autotools configuration"""
    return {
        'actions': [
            CmdAction('autoreconf -vis', cwd='libnfc'),
        ],
        'file_dep': ['libnfc/configure.ac',],
        'targets': ['libnfc/configure',],
        'verbosity': 2,
    }

def task_libnfc_configure():
    """Configures libnfc for building with autoconf"""
    return {
        'actions': [
            CmdAction('./configure --with-drivers=pn532_i2c,pn532_spi,pn532_uart,pn53x_usb --prefix=/usr --sysconfdir=/etc', cwd='libnfc'),
            ],
        'file_dep': ['libnfc/configure',],
        'targets': ['libnfc/Makefile',],
        'verbosity': 2,
    }

def task_libnfc_build():
    """Builds libnfc"""
    return {
        'actions': [
            CmdAction('make', cwd='libnfc'),
        ],
        'file_dep': ['libnfc/Makefile',],
        'targets': ['libnfc/utils/nfc-list',],
        'verbosity': 2,
    }

def task_libnfc_install():
    """Installs libnfc"""
    return {
        'actions': [
            CmdAction('sudo make install', cwd='libnfc'),
        ],
        'file_dep': ['libnfc/utils/nfc-list',],
        'targets': ['/usr/bin/nfc-list',],
    }

def task_libnfc_install_config():
    """Install sample configs and devices"""
    return {
        'actions': [
            CmdAction('sudo mkdir -p /etc/nfc'),
            CmdAction('sudo mkdir -p /etc/nfc/devices.d'),
            CmdAction('sudo cp libnfc/libnfc.conf.sample /etc/nfc/libnfc.conf'),
            CmdAction('sudo cp contrib/libnfc/pn532_i2c_on_rpi.conf /etc/nfc/devices.d/pn532_i2c_on_rpi.conf'),
        ],
        'file_dep': [
            '/usr/bin/nfc-list',
            'contrib/libnfc/pn532_i2c_on_rpi.conf',
        ],
        'targets': [
            '/etc/nfc/libnfc.conf',
            '/etc/nfc/devices.d/pn532_i2c_on_rpi.conf',
        ]
    }

if __name__ == '__main__':
    import doit
    doit.run(globals())
