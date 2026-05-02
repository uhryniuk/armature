.PHONY: release

release:
	uv version --bump patch
	git commit -am "chore: bump version to $$(uv version)"
	git tag "v$$(uv version)"
	git push && git push --tags
