using System;
using System.Threading.Tasks;
using Godot;
using MegaCrit.Sts2.Core.Bindings.MegaSpine;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.GodotExtensions;

namespace MegaCrit.Sts2.Core.Helpers;

public static class SpineNodeExtensions
{
	private const int _spineReadyWarnThresholdFrames = 600;

	public static void RunWhenSpineReady(this Node host, MegaSprite sprite, Action<MegaAnimationState> onReady)
	{
		TaskHelper.RunSafely(WaitForSpineReady(host, sprite, onReady));
	}

	private static async Task WaitForSpineReady(Node host, MegaSprite sprite, Action<MegaAnimationState> onReady)
	{
		int framesWaited = 0;
		while (GodotObject.IsInstanceValid(sprite.BoundObject) && !sprite.IsAnimationStateReady())
		{
			await host.AwaitProcessFrame();
			int num = framesWaited + 1;
			framesWaited = num;
			if (num == 600)
			{
				Log.Warn($"{host.Name}: still waiting for a SpineSprite skeleton after {framesWaited} " + "frames; its animation will not start until the skeleton loads (possible asset load failure).");
			}
		}
		if (GodotObject.IsInstanceValid(sprite.BoundObject))
		{
			onReady(sprite.GetAnimationState());
		}
	}
}
