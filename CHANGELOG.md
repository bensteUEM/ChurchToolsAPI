# Changelog

## [2.0.1](https://github.com/bensteUEM/ChurchToolsAPI/compare/v2.0.0...v2.0.1) (2025-07-20)


### Bug Fixes

* **event_agenda:** get_event_agenda_docx ([cc6f9b0](https://github.com/bensteUEM/ChurchToolsAPI/commit/cc6f9b0c5e80f58813efd1e120975e84bb9bfce9))
* **persons:** NULL value for sexId ([978d021](https://github.com/bensteUEM/ChurchToolsAPI/commit/978d0214d06471917b29a84ff68e9f489afb19be))

## [2.0.0](https://github.com/bensteUEM/ChurchToolsAPI/compare/v1.8.0...v2.0.0) (2025-05-20)


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
* **groups:** implement get_groups params passthrough and pre-test cleanup ([1de0b28](https://github.com/bensteUEM/ChurchToolsAPI/commit/1de0b2836d2abbc0b645b3cc7b3affce806fcc9b))
* **misc:** introduced ratelimited api requests ([#37](https://github.com/bensteUEM/ChurchToolsAPI/issues/37)) ([4ccc96b](https://github.com/bensteUEM/ChurchToolsAPI/commit/4ccc96b7b3bfdbb5ca2f116328ad6fbe21d47e13))
* **songs:** implement set_default_arrangement and fix sourceReference and sourceName ([#144](https://github.com/bensteUEM/ChurchToolsAPI/issues/144)) ([#272](https://github.com/bensteUEM/ChurchToolsAPI/issues/272)) ([10c5d19](https://github.com/bensteUEM/ChurchToolsAPI/commit/10c5d1902c4abc93b3b99dd7d42ec37ca6b9a0d0))
* **songs:** moved delete_song_arrangement from AJAX to REST ([#152](https://github.com/bensteUEM/ChurchToolsAPI/issues/152)) ([db696c9](https://github.com/bensteUEM/ChurchToolsAPI/commit/db696c998ce22cab2580cd59ad773e9388653e5c))
* **songs:** removed legacy get_song_ajax ([#151](https://github.com/bensteUEM/ChurchToolsAPI/issues/151)) ([4541e16](https://github.com/bensteUEM/ChurchToolsAPI/commit/4541e16622e4c7c2083bc3fb3535521b71ef702a))
* **songs:** updated use of create edit and delete with REST api incl. arrangements ([#143](https://github.com/bensteUEM/ChurchToolsAPI/issues/143),[#144](https://github.com/bensteUEM/ChurchToolsAPI/issues/144)) ([fad91ee](https://github.com/bensteUEM/ChurchToolsAPI/commit/fad91ee73f4ecff3536e854e460259e790580b5b))
* **tags:** migrated tags to new API ([#49](https://github.com/bensteUEM/ChurchToolsAPI/issues/49); [#142](https://github.com/bensteUEM/ChurchToolsAPI/issues/142)) ([e431a08](https://github.com/bensteUEM/ChurchToolsAPI/commit/e431a087ff136b1ef6e8bff6dae75b80d33bc275))
* **tags:** updated tags API and usage ([#142](https://github.com/bensteUEM/ChurchToolsAPI/issues/142)) ([af2b606](https://github.com/bensteUEM/ChurchToolsAPI/commit/af2b606bd0dbd01f4e1b191e13753c997165b9ad))


### Bug Fixes

* **calendar:** implemented workaround for API changes ([#141](https://github.com/bensteUEM/ChurchToolsAPI/issues/141)) ([701e443](https://github.com/bensteUEM/ChurchToolsAPI/commit/701e443356f84c66da5a21743cf89f4ee0b598e2))
* **calendar:** removed workaround because bug is feature (trunkcate seconds) [#141](https://github.com/bensteUEM/ChurchToolsAPI/issues/141) ([9b42ea0](https://github.com/bensteUEM/ChurchToolsAPI/commit/9b42ea0319b1deec65f7388340038724298ec705))
* **events:** test_get_set_event_services_counts ([#140](https://github.com/bensteUEM/ChurchToolsAPI/issues/140)) ([94f144b](https://github.com/bensteUEM/ChurchToolsAPI/commit/94f144b6962413775a9691dea9828d7b91b703f6))
* **files:** sample key references ([#140](https://github.com/bensteUEM/ChurchToolsAPI/issues/140)) ([af8a472](https://github.com/bensteUEM/ChurchToolsAPI/commit/af8a472c3b27baa62968447c8c2d42b4f3179835))
* **groups:** updated to more recent API behaviour ([#140](https://github.com/bensteUEM/ChurchToolsAPI/issues/140)) ([8ac3f9e](https://github.com/bensteUEM/ChurchToolsAPI/commit/8ac3f9e74b6e188d5251dc9ec43ebce11daccbc5))
* **misc:** increased number of attempts for ratelimited session because of github action  speed ([#37](https://github.com/bensteUEM/ChurchToolsAPI/issues/37)) ([9783061](https://github.com/bensteUEM/ChurchToolsAPI/commit/9783061585a9ad9d6df38bc6208e1286e35c12bb))
* **posts:** updated tests and changed pagination ([#145](https://github.com/bensteUEM/ChurchToolsAPI/issues/145)) ([e7788cd](https://github.com/bensteUEM/ChurchToolsAPI/commit/e7788cdbbee33be7f48d6d40b33b16699c20648d))
* repeat requests after timeout with too_many_requests  ([#37](https://github.com/bensteUEM/ChurchToolsAPI/issues/37)) ([ecd58c3](https://github.com/bensteUEM/ChurchToolsAPI/commit/ecd58c3f389d44769f67d135a519c5029c20dad1))
* **resources:** updated resource keys in test ([#146](https://github.com/bensteUEM/ChurchToolsAPI/issues/146)) ([a1c5c5d](https://github.com/bensteUEM/ChurchToolsAPI/commit/a1c5c5de3494d88c3700d0a9ede0165de95b2d81))
* **songs:** corrected dtypes ([#144](https://github.com/bensteUEM/ChurchToolsAPI/issues/144)) ([10c5d19](https://github.com/bensteUEM/ChurchToolsAPI/commit/10c5d1902c4abc93b3b99dd7d42ec37ca6b9a0d0))

## [1.8.0](https://github.com/bensteUEM/ChurchToolsAPI/compare/1.7.3...v1.8.0) (2025-05-17)


### Features

* implemented release automation ([#154](https://github.com/bensteUEM/ChurchToolsAPI/issues/154)) ([5496625](https://github.com/bensteUEM/ChurchToolsAPI/commit/5496625d1d1e92fed4b72d13aab6cb807941c4cf))
