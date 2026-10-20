# Publishing the hub

The hub is published at
[bishoku/agent-plugin-hub](https://github.com/bishoku/agent-plugin-hub).
Use this checklist when releasing updates.

1. Prepare changes in a branch and bump changed plugin versions and matching
   catalog entries. Document breaking changes.
2. Run the validation and export tests. Import the example into YADA and inspect
   the layout and playback. Test catalog discovery and installation in each
   client you advertise, using a fresh installation.
3. Review included licenses and notices. Check that plugin repository and
   homepage metadata point to the correct public URLs.
4. Open a pull request against `bishoku/agent-plugin-hub` and merge the reviewed
   changes after validation passes. To start from a fresh checkout:

   ```sh
   git clone https://github.com/bishoku/agent-plugin-hub.git
   cd agent-plugin-hub
   ```

5. Confirm GitHub Actions passes. Enable branch protection and require the
   validation job for pull requests.
6. Tag a reviewed release, for example `yada-v1.0.0`, and publish release notes
   listing client versions tested and known limitations.

Users refresh the marketplace and update their installed copy; editing the
GitHub source alone may not refresh an assistant's cached plugin.

Hosting a public repository does not automatically list it in an assistant's
central plugin directory. Users add this repository as a marketplace source.
