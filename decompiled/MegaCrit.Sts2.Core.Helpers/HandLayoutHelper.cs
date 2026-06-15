using System.Collections.Generic;

namespace MegaCrit.Sts2.Core.Helpers;

public static class HandLayoutHelper
{
	public static int GetInsertIndex<T>(IReadOnlyList<T> pileOrder, IEnumerable<T> presentCards, T target)
	{
		EqualityComparer<T> equalityComparer = EqualityComparer<T>.Default;
		int num = IndexOf(pileOrder, target, equalityComparer);
		if (num < 0)
		{
			return -1;
		}
		int num2 = 0;
		foreach (T presentCard in presentCards)
		{
			if (!equalityComparer.Equals(presentCard, target))
			{
				int num3 = IndexOf(pileOrder, presentCard, equalityComparer);
				if (num3 >= 0 && num3 < num)
				{
					num2++;
				}
			}
		}
		return num2;
	}

	private static int IndexOf<T>(IReadOnlyList<T> list, T item, EqualityComparer<T> comparer)
	{
		for (int i = 0; i < list.Count; i++)
		{
			if (comparer.Equals(list[i], item))
			{
				return i;
			}
		}
		return -1;
	}
}
