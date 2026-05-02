.PHONY: release

release:
	uv version --bump patch
	git commit -am "chore: bump version to $$(uv version | cut -d' ' -f2)"
	git tag "v$$(uv version | cut -d' ' -f2)"
	git push && git push --tags
