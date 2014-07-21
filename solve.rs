use std::rc::Rc;
use std::num::abs;
use std::collections::HashMap;
//use std::collections::PriorityQueue;

type N = int;
type Parent = Option<Rc<Node>>;
type Matrix = Rc<Vec<N>>;
type Shape = (N, N);
type Value = int;
static X: N = 3;
static Y: N = 3;


enum Step
{
    Start = 0,
    Left = 1,
    Right = 2,
    Up = 3,
    Down = 4,
}

struct Node
{
    matrix: Matrix,
    shape: Shape,
    parent: Parent,
    center: N,
    depth: N,
    value: Value,
    step: Step,
}

impl Node
{
    fn new(parent: Rc<Node>, matrix: Matrix, step: Step, center: N) -> Node
    {
        let value = Node::valuation(matrix.clone(), parent.shape);
        Node {
            matrix: matrix,
            shape: parent.shape,
            parent: Some(parent.clone()),
            center: center,
            depth: parent.depth + 1,
            value: value,
            step: step,
        }
    }

    fn new_root(matrix: Matrix, shape: Shape, center: N) -> Node
    {
        let value = Node::valuation(matrix.clone(), shape);
        Node {
            matrix: matrix,
            shape: shape,
            center: center,
            depth: 0,
            value: value,
            step: Start,
            parent: None,
        }
    }

    fn valuation(matrix: Matrix, shape: Shape) -> Value
    {
        let mut value = 0i;
        let (x, y) = shape;
        for i in range(0, x*y) {
            let a = matrix.get(i as uint);
            value += abs(i/y - a/y) + abs((i % y) - (a % y));
        }
        value as Value
    }

    fn print(&self)
    {
        println!("matrix: {} value: {}", self.matrix.as_slice(), self.value);
    }
}


//impl Ord for Node
//{
//    fn cmp(&self, other: &Node) -> Ordering{
//        if self.value > other.value {Greater} else {Less}
//    }
//}
//impl Eq for Node {}
//impl PartialEq for Node {}
//impl PartialOrd for Node
//{
//    // fn partial_cmp(&self, other: &Self) -> Option<Ordering>;
//
//    // fn lt(&self, other: &Self) -> bool { ... }
//    // fn le(&self, other: &Self) -> bool { ... }
//    // fn gt(&self, other: &Self) -> bool { ... }
//    // fn ge(&self, other: &Self) -> bool { ... }
//}

fn spread(parent: Rc<Node>, step: Step) -> Option<Rc<Node>>
{
    let (x, y) = parent.shape;
    let max = x*y;
    let center = parent.center;
    let mut matrix = parent.matrix.deref().clone();
    let shift = match step {
        Up => {
            let shift = center - x;
            if shift >= 0 {Some(shift)} else {None}
        },
        Down => {
            let shift = center + x;
            if shift < max {Some(shift)} else {None}
        },
        Left => {
            let shift = center - 1;
            if center % y != 0 {Some(shift)} else {None}
        },
        Right => {
            let shift = center + 1;
            if shift % y != 0 {Some(shift)} else {None}
        },
        Start => fail!("Start?")
    };
    match shift {
        None => None,
        Some(shift) => {
            {
                let c = center as uint;
                let s = shift as uint;
                let matrix_slice = matrix.as_mut_slice();
                let swap = matrix_slice[c];
                matrix_slice[c] = matrix_slice[s];
                matrix_slice[s] = swap;
            }
            Some(Rc::new(Node::new(parent, Rc::new(matrix), step, shift)))
        }
    }
}


fn add(open: &mut Vec<Rc<Node>>, node: Rc<Node>) -> () {
    let step = [Up, Down, Left, Right];
    for i in range(0u, 4) {
        match spread(node.clone(), step[i]) {
            None => {},
            Some(new_node) => {open.push(new_node);}
        };
    };
}

fn solve(root: Rc<Node>) -> Rc<Node>
{
    let mut open: Vec<Rc<Node>> = Vec::new();
    let mut close = HashMap::new();
    let mut solve_node = root.clone();
    let max_loop = 10000u;
    open.push(root);
    for _ in range(0, max_loop) {
        match open.pop() {
            None => fail!("open empty"),
            Some(node) => {
                let value = node.value;
                if value == 0 {return node;}
                else if close.contains_key(&node.matrix) {continue;} // TODO: update
                else {close.insert(node.matrix.clone(), node.clone());}
                if node.value < solve_node.value {solve_node = node.clone()};
                add(&mut open, node);
            }
        }
        open.sort_by(|a, b| b.value.cmp(&a.value));
    }
    solve_node
}

fn main()
{
    let root = Rc::new(Node::new_root(Rc::new(vec!(4, 1, 2, 3, 0, 5, 6, 8, 7, 9)), (X, Y), 0));
    solve(root).print()
}
