import java.util.Comparator;

public class StateCompare implements Comparator<PuzzleState> {

	@Override
	public int compare(PuzzleState o1, PuzzleState o2) {
		return (o1.get_f() > o2.get_f()) ? 1 : 0;
	}
}
