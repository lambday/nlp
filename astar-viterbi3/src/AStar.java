import java.io.FileNotFoundException;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.ListIterator;
import java.util.Iterator;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

class PuzzleState implements Comparable<PuzzleState> {
	
	//TODO Add variables describing the state
	PuzzleState parent;
	PuzzleState goal;
	int tagindex;
	int dist;
	static double MINVAL;
	static double PUNMIN;
	double costToChild;
	public static final int MAXNEXT = 61;//61
	public static final int GOALID = 29;//29 for PUN
	public static double[][] ttable;
	public static HashMap<String, double[]> etable;
	public static String[] sentence;
	public String word;

	// initializing MINVAL
	public static void initMinval( double val ) { MINVAL = val; }
	// initializing PUNMIN
	public static void initPunMin( double val ) { PUNMIN = val; }
	// initializing transition table
	public static void initTtable() {
		ttable = new double[MAXNEXT + 1][MAXNEXT];
		for ( int i = 0; i <= MAXNEXT; ++i ) {
			for ( int j = 0; j < MAXNEXT; ++j ) {
				ttable[i][j] = 0.0;
			}
		}
	}
	// printing transition table
	public static void printTtable() {
		for ( int i = 0; i <= MAXNEXT; ++i ) {
			for ( int j = 0; j < MAXNEXT; ++j ) {
				System.out.print( ttable[i][j] + " " );
			}
			System.out.println();
		}
	}
	// initializing etable
	public static void initEtable() { etable = new HashMap<String, double[]>(); }
	// printing emission table
	public static void printEtable() {
		for ( Iterator i = etable.entrySet().iterator(); i.hasNext(); ) {
			Map.Entry me = (Map.Entry)i.next();
			String key = (String) me.getKey();
			System.out.print(key + ": ");
			double[] list = etable.get(key);
			for ( int k = 0; k < MAXNEXT; ++k )
				System.out.print( list[k] + " " );
			System.out.println();
		}
	}
	
	/** Construction **/
	public PuzzleState() {
		parent = null;
		goal = null;
		dist = 0;
		tagindex = -1;
		word = "^";
	}
	
	public void set( PuzzleState p, PuzzleState g, int d, int t, double c, String w ) {
		this.parent = p;
		this.goal = g;
		this.dist = d;
		this.tagindex = t;
		this.costToChild = c;
		this.word = w;
	}
	
	public void set(PuzzleState p) {
		//TODO Set variables describing state to corresponding values of state p	
		parent = p.parent;
		goal = p.goal;
		this.dist = p.dist;
		this.tagindex = p.tagindex;
		this.costToChild = p.costToChild;
		this.word = p.word;
	}
	
	public PuzzleState get_copy() {
		PuzzleState copy = new PuzzleState();
		//TODO Copy current state variable values to copy
		copy.parent = parent;
		copy.goal = goal;
		copy.dist = dist;
		copy.tagindex = tagindex;
		copy.costToChild = costToChild;
		copy.word = word;
		return copy;
	}
	
	@Override
	public boolean equals( Object o ) {
		if ( o != null && o instanceof PuzzleState ) {
			PuzzleState p = (PuzzleState) o;
			return (( dist == p.dist && tagindex == p.tagindex ));
		} else { return false; }
		// Return false if any of the state variables are not equal for current state and state p
		// TODO REMOVE THE FOLLOWING LINE
		//System.out.println( "not equal " + tagindex + "," + p.tagindex + " dist " + dist + "," + p.dist );
		//

	}
	
	public int  distance(PuzzleState p) {
		// Return the estimated distance from p to the goal node (instead of 1)
		return dist;
	}
	
	public boolean safe(int missionaries, int cannibals) //TODO Arguments: variables describing the state
	{
		//TODO Return true if the variables define a valid state, else false 
		return false;
	}
	
	public PuzzleState  state1( double[] costList, int n ) {
		if ( dist == 1 ) {
			return goal;
		}
		PuzzleState copy = this.get_copy();
		// Generate next state from current state by suitable modifications of the variables
		//(make as many copies of this function as number of possible transitions from a given state)
		copy.dist = dist - 1;
		copy.parent = null;///CHANGED FROM 'THIS' TO 'NULL'
		copy.word = sentence[sentence.length + 1 - dist];
		copy.tagindex = -1;
		/*
		for ( int i = 0; i < costList.length; ++i ) {
			System.out.println( "costlist =>" + costList[i] );
		}
		System.out.println( n );
		System.exit(0);
		*/
		try {
			copy.costToChild = costList[n];
			//System.out.println( "cost to child updated for child" + costList[n] );
		} catch( ArrayIndexOutOfBoundsException e ) {
			//e.printStackTrace();
			//TODO REMOVE THE FOLLOWING LINE
			//System.out.println( n );
			//
			//System.out.println( copy.dist + "==>cost to child taken as " + PUNMIN );
			copy.costToChild = PUNMIN;
		}
		//TODO REMOVE THE FOLLOWING LINE
		//System.out.println( copy.costToChild );
		//
		return copy;
	}
	
	//TODO CHANGE THE SHIT, THIS IS THE ACTUAL COST
	public double get_g() {
		double g = 0;
		PuzzleState current = this;
		while( current.parent != null ) {
			//g += 10;//TODO
			double t = ttable[current.parent.tagindex][current.tagindex];
			double e = etable.get(current.word)[current.tagindex];
			double m = e * t;
			if ( m != 0.0 ) {
				g += -java.lang.Math.log(m);
			} else {
				g += java.lang.Integer.MAX_VALUE;
			}
			current = current.parent;
		}
		//System.out.println( g );
		//System.exit(0);
		return g;
	}
	
	// THIS IS THE HEURISTIC
	public double get_h() {
/*
		double h = costToChild;
		if ( dist > 1 ) h += PUNMIN;
		for ( int i = 1; i < dist - 1; ++i ) {
			h += MINVAL;
		}
		//System.out.print( "<dist:" + dist + ",h:" + h + ">" );
		return h;
*/		
		return 0.0;
	}
    
	public double get_f() {
		return this.get_g() + this.get_h();
	}
    
	public ArrayList<PuzzleState> get_child_list( double[] costList, int N ) {
		ArrayList<PuzzleState> ch_list = new ArrayList<PuzzleState>();
		if ( dist != 0 ) {
			if ( dist == 1 ){
				ch_list.add( goal );
			} else {
				for ( int i = 0; i < MAXNEXT; ++i ) {	// 61 is the total number of possible next states
					PuzzleState start1 = this.state1( costList, N - dist );
					start1.tagindex = i;
					if(false == this.equals(start1)&&(parent == null || false == parent.equals(start1)))
						ch_list.add( start1 );
				}
			}
		}
		return ch_list;
	}
    
	public void print() {
		System.out.println( /*"print called " +*/ tagindex );
	}
	
	public void print_path() {
		int len = 0;
		this.print();
		PuzzleState current = parent;
		while( current != null ) {
			++len;
			current.print();
			current = current.parent;
		}
		//System.out.println("Length of Optimal Path :"+len);
	}
	
	@Override
	public int compareTo(PuzzleState arg0) {
		double my_g = this.get_g();
		double my_h = this.get_h();
		double her_g = arg0.get_g();
		double her_h = arg0.get_h();
		return ((my_g+my_h) > (her_g+her_h)) ? 1 : 0;
	}
	
	/*
	@Override
	public boolean equals(Object o) {
		if( ! (o instanceof PuzzleState) ) 
			return false;
		PuzzleState p = (PuzzleState)o;
		//TODO Return true if current state equals state p
		return false;
	}
	*/
}

public class AStar {
	
	static ArrayList<PuzzleState> OpenList;
	static ArrayList<PuzzleState> ClosedList;
	static PuzzleState goal = null;
	static boolean closed_parent_update = false;//TODO CHANGE IT TO FALSE
	static double BSmin, PunMin;
	static double[] costList;

	public static double getCost( PuzzleState node, PuzzleState n_par ) {
		double cost;
		double t = PuzzleState.ttable[n_par.tagindex][node.tagindex];
		double e = PuzzleState.etable.get(node.word)[node.tagindex];
		double m = e * t;
		if ( m != 0.0 ) {
			cost = -java.lang.Math.log(m);
		} else {
			cost = java.lang.Integer.MAX_VALUE;
		}
		return cost;
	}
	
	public static boolean parent_update_recr(PuzzleState node,PuzzleState n_par) {
		if( node.get_g() > ( n_par.get_g() + getCost(node, n_par) ) ){
			node.parent = n_par;
		//	System.out.println( node.get_g() + "," + n_par.get_g() + "," + getCost(node,n_par) );
		} else {
			return false;
		}
		boolean retval = false;
		ArrayList<PuzzleState> ch_list = node.get_child_list(costList, costList.length + 2);
		for( ListIterator<PuzzleState> it = ch_list.listIterator() ; it.hasNext(); ) {
			PuzzleState ch = it.next();
			ch.print();
			if(true == ClosedList.contains(ch)) {
				closed_parent_update = true;
				parent_update_recr(ch,node);
				retval = true;
			}
		}
		return retval;
	}
	
	public static void main(String[] args) throws FileNotFoundException{
		BufferedReader br = null;
	
		if( args.length < 2 ) {
			System.out.println( "Error: Wrong format" );
			System.exit(1);
		} 
		BSmin = Double.parseDouble(args[0]);
		PunMin = Double.parseDouble(args[args.length-1]);
		costList = new double[args.length-2];
		for ( int i = 1; i < args.length -1; ++i ) {
			costList[i-1] = Double.parseDouble(args[i]);
		}
		double[] temp = costList;
		Arrays.sort( temp );
		PuzzleState.initMinval( temp[0] );
		PuzzleState.initPunMin( PunMin );

		// init ttable
		PuzzleState.initTtable();
//		PuzzleState.printTtable();
		try {
			String sCurrentLine; 
			br = new BufferedReader(new FileReader( "./tag"  ));
			int line = 0;
			while ((sCurrentLine = br.readLine()) != null) {
				String[] list = sCurrentLine.split(",");
				//System.out.println( list[list.length-1] );
				for ( int col = 0; col < list.length; ++col ) {
					PuzzleState.ttable[line][col] = Double.parseDouble(list[col]);
				}
				line++;
			}
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			try {
				if (br != null)br.close();
			} catch (IOException ex) {
				ex.printStackTrace();
			}
		}
		//PuzzleState.printTtable();
		// initialize the sentence
		ArrayList<String> sentence = new ArrayList<String>();
		// initialize emission table
		PuzzleState.initEtable();
		try {
			String sCurrentLine; 
			br = new BufferedReader(new FileReader( "./emps"  ));//TODO
			int line = 0;
			while ((sCurrentLine = br.readLine()) != null) {
				String[] keyval = sCurrentLine.split(":");
				String[] list = keyval[1].split(" ");
				//System.out.println( list[list.length-1] );
				double[] val = new double[list.length];
				for ( int col = 0; col < list.length; ++col ) {
					val[col] = Double.parseDouble(list[col]);
				}
				PuzzleState.etable.put( keyval[0], val );
				sentence.add( keyval[0] );
				line++;
			}
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			try {
				if (br != null)br.close();
			} catch (IOException ex) {
				ex.printStackTrace();
			}
		}

		//PuzzleState.printEtable();
		String[] tmp = sentence.toArray(new String[sentence.size()]);
		int len = sentence.size();
		String lastword = tmp[(len - 1)];
		PuzzleState.sentence = Arrays.copyOfRange(tmp, 0, (len - 1));
		//PuzzleState.printEtable();
		/*
		for ( int i = 0; i < PuzzleState.sentence.length; ++i ) {
			System.out.println( PuzzleState.sentence[i] );
		}*/
//		System.exit(0);
		
		/* TEST
		System.out.println( BSmin + "," + PunMin );
		for ( int i = 0; i < costList.length; ++i ) {
			System.out.println( costList[i] );
		}
		*/
	
		OpenList = new ArrayList<PuzzleState>();
		ClosedList = new ArrayList<PuzzleState>();

		PuzzleState start = new PuzzleState();
		goal = new PuzzleState();
		
		start.set( null, goal, args.length, PuzzleState.MAXNEXT, BSmin, "^" );
		goal.set( null, goal, 0, PuzzleState.GOALID, 0.0, lastword );
		start.goal = goal;
		
		int no_of_step = 0;
		OpenList.add(start);
		//TODO REMOVE
		start.get_h();
		//
		while( false == OpenList.isEmpty()) {
			++no_of_step;
			PuzzleState node = OpenList.get(0);
			//node.print();
			
			if(true == node.equals(goal)) {
				//System.out.println("\n\nGoal Reached !!");
				//node.print();
				//System.out.println("\nTotal number of steps :"+no_of_step);
				if(true == closed_parent_update)
					System.out.println("\nParent updated in closed list!!");
				node.print_path();
				//System.out.println( node.get_g() );
				return;
			}
			OpenList.remove(0);
			ClosedList.add(node);
//			System.out.println( "current node " + node.word + ":" + node.tagindex + "g=" + node.get_g() );
			ArrayList<PuzzleState> ch_list = node.get_child_list( costList, args.length );
			//TODO REMOVE
			//System.out.println( "children " + ch_list.size() );
			//
			for( ListIterator<PuzzleState> it = ch_list.listIterator() ; it.hasNext(); ) {
				PuzzleState ch = it.next();
				// TODO REMOVE
				//System.out.println( "distance from goal " + ch.dist );
				//
				if(false == ClosedList.contains(ch)) {
					//System.out.print( "cl does not contain " + ch.word );
					//System.out.println( ch.tagindex );
					if(false == OpenList.contains(ch)) {
						OpenList.add(ch);
						ch.parent = node;
					//	System.out.print( "ol does not contain, adding " + ch.word );
					//	System.out.println( ch.tagindex );
					} else {
					//	System.out.print( "ol contains " + ch.word );
					//	System.out.println( ch.tagindex );
						
						/// get the instance in the OpenList
						PuzzleState pch = OpenList.get(OpenList.indexOf(ch));
						if(pch.get_g() > node.get_g() + getCost(pch,node)) {
						//	System.out.print( "for ch:" + pch.word + pch.tagindex );
						//	System.out.print( " old g = " + pch.get_g() + "," );
						//	System.out.println( "new g = " + (node.get_g()+getCost(pch,node)) );
							pch.parent = node;
						}
					}
				} else {
				//	System.out.print( "cl contains " + ch.word );
				//	System.out.println( ch.tagindex );
					PuzzleState pch = ClosedList.get(ClosedList.indexOf(ch));
					parent_update_recr(pch,node);
				}
			}
			//TODO REMOVE
			//System.out.println( "openlist has " + OpenList.size() );
			//System.out.println( "closedlist has " + ClosedList.size() );
			//
			Collections.sort(OpenList, new StateCompare());
		}
		System.out.println("Open List Empty: Problem unsolvable");
	}
}

