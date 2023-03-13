#!/bin/bash
export TWINE_PASSWORD=dolce91PYPI
export TWINE_USERNAME=smathot
rm -Rf deb_dist dist build
# First to the PPA
python setup.py --command-packages=stdeb3.command bdist_deb
cd deb_dist
debsign -kBC4DA589EDBC162D450778AAA410716F12FFDA5C *_source.changes
dput ppa:smathot/rapunzel *_source.changes
cd ..
python setup.py sdist
python setup.py bdist_wheel
twine upload dist/*.tar.gz
twine upload dist/*.whl
