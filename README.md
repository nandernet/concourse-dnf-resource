# concourse-dnf-resource
Concourse Resource Type for tracking changes in DNF repositories. An essential
tool for ensuring you're consistently providing up-to-date fedora or UBI based
images.

![CI](https://ci.nic-a.net/api/v1/teams/main/pipelines/concourse-dnf-resource/badge)

### How to use

This example is derived straight from this repository, within 
`ci/pipeline.yaml`! The rest of this example assume you're using
`quay.io/fedora/fedora-minimal` as your base image. Later samples will showcase
how this could be done with other Yum/DNF based distributions like RedHat's UBI
or Amazon Linux.

First, you will first need to define the resource_type for your pipelines:

```yaml
resource_types:
- name: dnf-resource
  type: registry-image
  source:
    repository: ghcr.io/nanderson94/concourse-dnf-resource
    tag: latest
```

Note that this image is also available via 
[Docker Hub](https://hub.docker.com/r/nandernet/concourse-dnf-resource) and 
[Quay.io](https://quay.io/nandernet/concourse-dnf-resource).

Next, you define your DNF dependencies as resources:

```yaml
resources:
  - name: fedora-updates-python3
    type: dnf-resource
    check_every: 4h
    source:
      repositories:
        - https://ftp-chi.osuosl.org/pub/fedora/linux/releases/38/Everything/x86_64/os/
        - https://ftp-chi.osuosl.org/pub/fedora/linux/updates/38/Everything/x86_64/
      package: python3
```

The `repositories` key is a repository baseurl, like what you would typically
find within a mirrorlist file or metalink entry. A tailing slash is expected,
and you should find a `repodata/repomd.xml` file within. The `package` key is
any package or sub-package you require during the build/runtime of your image.
The package is **not** downloaded as part of this resource.

Finally, configure your new resource to trigger new builds of your images:

```yaml
jobs:
  - name: image-build
    plan:
      - in_parallel:
        - get: fedora-updates-python3
          trigger: true
```

### Pathway to 1.x

* [ ] Support mirrorlist and metalink dereferencing to broaden support.
* [ ] Document and validate usage with other Yum/DNF distros.
* [ ] Unit / Functional testing before publication of updated images.


