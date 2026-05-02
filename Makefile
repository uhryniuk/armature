.PHONY: release release-patch release-minor release-major

release: release-patch

release-patch:
	uv version --bump patch
	git commit -am "chore: bump version to $$(uv version | cut -d' ' -f2)"
	git tag "v$$(uv version | cut -d' ' -f2)"
	git push && git push --tags

release-minor:
	uv version --bump minor
	git commit -am "chore: bump version to $$(uv version | cut -d' ' -f2)"
	git tag "v$$(uv version | cut -d' ' -f2)"
	git push && git push --tags

release-major:
	uv version --bump major
	git commit -am "chore: bump version to $$(uv version | cut -d' ' -f2)"
	git tag "v$$(uv version | cut -d' ' -f2)"
	git push && git push --tags
