# Changelog

## [2.0.0](https://github.com/bensteUEM/ChurchToolsAPI/compare/v1.8.0...v2.0.0) (2025-05-17)


### ⚠ BREAKING CHANGES

* **events:** removed legacy test ([#148](https://github.com/bensteUEM/ChurchToolsAPI/issues/148))
* **events:** implemented update_event and replaced event admin tests respectively ([#150](https://github.com/bensteUEM/ChurchToolsAPI/issues/150))
* **songs:** removed legacy get_song_ajax ([#151](https://github.com/bensteUEM/ChurchToolsAPI/issues/151))
* **tags:** migrated tags to new API (#49; #142)
* **songs:** updated use of create edit and delete with REST api incl. arrangements (#143,#144)
* **tags:** updated tags API and usage ([#142](https://github.com/bensteUEM/ChurchToolsAPI/issues/142))

### Features

* **api:** Add a function to retrieve base url ([4082696](https://github.com/bensteUEM/ChurchToolsAPI/commit/408269601b44c6fc80a7bc214352187cf3707d61))
* **events:** implemented update_event and replaced event admin tests respectively ([#150](https://github.com/bensteUEM/ChurchToolsAPI/issues/150)) ([fe788d9](https://github.com/bensteUEM/ChurchToolsAPI/commit/fe788d9c10c7d44496209ef3e42e49f7f95f5dec))
* **events:** removed legacy test ([#148](https://github.com/bensteUEM/ChurchToolsAPI/issues/148)) ([74d21e4](https://github.com/bensteUEM/ChurchToolsAPI/commit/74d21e45c7d0dccc51044c7194bb4f7a5b8f0311))
* **misc:** introduced ratelimited api requests ([#37](https://github.com/bensteUEM/ChurchToolsAPI/issues/37)) ([4ccc96b](https://github.com/bensteUEM/ChurchToolsAPI/commit/4ccc96b7b3bfdbb5ca2f116328ad6fbe21d47e13))
* **songs:** moved delete_song_arrangement from AJAX to REST ([#152](https://github.com/bensteUEM/ChurchToolsAPI/issues/152)) ([db696c9](https://github.com/bensteUEM/ChurchToolsAPI/commit/db696c998ce22cab2580cd59ad773e9388653e5c))
* **songs:** removed legacy get_song_ajax ([#151](https://github.com/bensteUEM/ChurchToolsAPI/issues/151)) ([4541e16](https://github.com/bensteUEM/ChurchToolsAPI/commit/4541e16622e4c7c2083bc3fb3535521b71ef702a))
* **songs:** updated use of create edit and delete with REST api incl. arrangements ([#143](https://github.com/bensteUEM/ChurchToolsAPI/issues/143),[#144](https://github.com/bensteUEM/ChurchToolsAPI/issues/144)) ([fad91ee](https://github.com/bensteUEM/ChurchToolsAPI/commit/fad91ee73f4ecff3536e854e460259e790580b5b))
* **tags:** migrated tags to new API ([#49](https://github.com/bensteUEM/ChurchToolsAPI/issues/49); [#142](https://github.com/bensteUEM/ChurchToolsAPI/issues/142)) ([e431a08](https://github.com/bensteUEM/ChurchToolsAPI/commit/e431a087ff136b1ef6e8bff6dae75b80d33bc275))
* **tags:** updated tags API and usage ([#142](https://github.com/bensteUEM/ChurchToolsAPI/issues/142)) ([af2b606](https://github.com/bensteUEM/ChurchToolsAPI/commit/af2b606bd0dbd01f4e1b191e13753c997165b9ad))


### Bug Fixes

* **calendar:** implemented workaround for API changes ([#141](https://github.com/bensteUEM/ChurchToolsAPI/issues/141)) ([701e443](https://github.com/bensteUEM/ChurchToolsAPI/commit/701e443356f84c66da5a21743cf89f4ee0b598e2))
* **calendar:** removed workaround because bug is feature (trunkcate seconds) [#141](https://github.com/bensteUEM/ChurchToolsAPI/issues/141) ([9b42ea0](https://github.com/bensteUEM/ChurchToolsAPI/commit/9b42ea0319b1deec65f7388340038724298ec705))
* **groups:** updated to more recent API behaviour ([#140](https://github.com/bensteUEM/ChurchToolsAPI/issues/140)) ([8ac3f9e](https://github.com/bensteUEM/ChurchToolsAPI/commit/8ac3f9e74b6e188d5251dc9ec43ebce11daccbc5))
* **posts:** updated tests and changed pagination ([#145](https://github.com/bensteUEM/ChurchToolsAPI/issues/145)) ([e7788cd](https://github.com/bensteUEM/ChurchToolsAPI/commit/e7788cdbbee33be7f48d6d40b33b16699c20648d))
* **resources:** updated resource keys in test ([#146](https://github.com/bensteUEM/ChurchToolsAPI/issues/146)) ([a1c5c5d](https://github.com/bensteUEM/ChurchToolsAPI/commit/a1c5c5de3494d88c3700d0a9ede0165de95b2d81))

## [1.8.0](https://github.com/bensteUEM/ChurchToolsAPI/compare/1.7.3...v1.8.0) (2025-05-17)


### Features

* implemented release automation ([#154](https://github.com/bensteUEM/ChurchToolsAPI/issues/154)) ([5496625](https://github.com/bensteUEM/ChurchToolsAPI/commit/5496625d1d1e92fed4b72d13aab6cb807941c4cf))
