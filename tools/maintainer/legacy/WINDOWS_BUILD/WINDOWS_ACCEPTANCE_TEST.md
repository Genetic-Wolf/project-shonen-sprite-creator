# Project Shonen Sprite Creator — Windows RC Acceptance Test

Do not call the release production-ready until this checklist passes on a Windows machine.

## Clean-machine launch
- Build `ProjectShonenSpriteCreator.exe` on Windows.
- Test the packaged artist folder on a Windows account that does not rely on the development Python environment.
- Confirm the Creator launches by double-clicking the EXE.
- Confirm no console, pip, Python, or JSON editing is required by the artist.

## Body-master gate
- Open Female Standard and Male Standard.
- Replace/confirm the TV master artwork visually.
- Approve + Lock only after feet, centerline, frame grid, directions and animation alignment are correct.
- Confirm character production is blocked while the relevant master output remains Draft/Unlocked.

## Clip Studio workflow
- Create a reusable piece.
- Generate each required ORA workspace.
- Open it in Clip Studio Paint.
- Confirm guide/reference/DRAW layers are visible and correctly aligned.
- Export transparent PNG without trimming.
- Import it into the Creator.
- Intentionally import one wrong-size PNG and confirm a clear error is shown.

## Character workflow
- Assemble a character.
- Verify live preview and layer ordering.
- Save the character project, close/reopen the Creator, and reopen the project.
- Verify body master, selected pieces and layer order survive.
- Export TV, FG, TVD and SV when their corresponding masters/pieces are complete.
- Confirm incomplete outputs are blocked.

## RPG Maker MZ
- Select a disposable MZ test project.
- Install outputs.
- Confirm TV/FG/TVD/SV appear in their expected game locations.
- Replace an existing same-name file and verify a timestamped backup is created.
- Launch the MZ test game and visually inspect walking animation, face graphic, downed graphic and SV battler.

## Failure rule
Any crash, silent data loss, misaligned canonical art, overwrite without backup, or need for the artist to edit source/JSON is a release-blocking defect.
