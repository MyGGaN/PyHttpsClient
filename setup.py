#!/usr/bin/env python
import distutils.core
import https_client

version = https_client.__version__

distutils.core.setup(
    name="https_client",
    version=version,
    packages=["https_client"],
    author="Fredrik Svensson",
    author_email="fredrik.svensson@mblox.com",
    url="",
    description="HTTPS client with ssl client auth support.",
    scripts=[],
)
