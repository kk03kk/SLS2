using System.Collections.Generic;
using Godot;
using Godot.Collections;

namespace MegaCrit.Sts2.Core.Bindings.MegaSpine;

public class MegaSkeletonDataResource : MegaSpineBinding
{
	protected override string SpineClassName => "SpineSkeletonDataResource";

	protected override IEnumerable<string> SpineMethods => new global::_003C_003Ez__ReadOnlyArray<string>(new string[4] { "find_animation", "find_skin", "get_animations", "get_skins" });

	public MegaSkeletonDataResource(Variant native)
		: base(native)
	{
	}

	public MegaSkin? FindSkin(string skinName)
	{
		Variant native = Call("find_skin", skinName);
		if (native.AsGodotObject() == null)
		{
			return null;
		}
		return new MegaSkin(native);
	}

	public bool HasAnimation(string animName)
	{
		return Call("find_animation", animName).AsGodotObject() != null;
	}

	public IReadOnlyList<string> GetAnimationNames()
	{
		Array<GodotObject> array = (Array<GodotObject>)Call("get_animations");
		List<string> list = new List<string>(array.Count);
		foreach (GodotObject item in array)
		{
			MegaAnimation megaAnimation = new MegaAnimation(item);
			list.Add(megaAnimation.GetName());
		}
		return list;
	}

	public Array<GodotObject> GetSkins()
	{
		return (Array<GodotObject>)Call("get_skins");
	}
}
