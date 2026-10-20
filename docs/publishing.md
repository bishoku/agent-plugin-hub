# Publishing the hub

The scaffold is local. Creating a public repository and pushing it are separate
actions performed by the maintainer.

1. Choose the GitHub owner and repository name. Replace `OWNER/REPO` in the root
   README with that destination.
2. Run the validation and export tests. Import the example into YADA and inspect
   the layout and playback. Test catalog discovery and installation in each
   client you advertise, using a fresh installation.
3. Review included licenses and notices. Add repository/homepage metadata to
   plugin manifests when the public URLs are known.
4. Create an empty public GitHub repository. From this directory:

   ```sh
   git init -b main
   git add .
   git commit -m "Add Agent Plugins 1.0 marketplace and YADA plugin"
   git remote add origin https://github.com/OWNER/REPO.git
   git push -u origin main
   ```

5. Confirm GitHub Actions passes. Enable branch protection and require the
   validation job for pull requests.
6. Tag a reviewed release, for example `yada-v1.0.0`, and publish release notes
   listing client versions tested and known limitations.

For later releases, bump changed package versions and matching catalog entries,
repeat tests, and document breaking changes. Users refresh the marketplace and
update their installed copy; editing the GitHub source alone may not refresh
an assistant's cached plugin.

Hosting a public repository does not automatically list it in an assistant's
central plugin directory. Users add this repository as a marketplace source.
