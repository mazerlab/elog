# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

def keyboard(banner='Type EOF/^D to continue'):
	"""Clone of the matlab keyboard() function.
	
	Drop down into interactive shell for debugging
    Use it like the matlab keyboard command -- dumps you into
    interactive shell where you can poke around and look at
	variables in the current stack frame
	
    The idea and code are stolen from something Fredrick
	Lundh posted on the web a while back.
    """

	import code, sys

	# use exception trick to pick up the current frame
	try:
		raise None
	except:
		frame = sys.exc_info()[2].tb_frame.f_back

	# evaluate commands in current namespace
	namespace = frame.f_globals.copy()
	namespace.update(frame.f_locals)

	code.interact(banner=banner, local=namespace)
