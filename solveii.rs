use std::os;
use std::rand::{task_rng, Rng};
use std::rc::Rc;
use std::num::abs;
use std::collections::{PriorityQueue, HashSet};

type A = u8;
type Shape = (A, A);
type Matrix = Vec<A>;


#[deriving(Clone, Eq, PartialEq)]
enum Step {
    Start,
    Select,
    Up,
    Right,
    Down,
    Left,
}


#[deriving(Clone, Eq, PartialEq)]
struct Node {
    matrix: Rc<Matrix>,
    shape: Shape,
    center: A,
    value: uint,
    parent: Option<Rc<Node>>,
    delay: Option<(A, A)>,
    step: Step,
    depth: uint,
}

impl PartialOrd for Node {
    fn lt(&self, other: &Node) -> bool {
        self.value > other.value
    }
}

impl Ord for Node {
    fn cmp(&self, other: &Node) -> Ordering {
        let result = other.value.cmp(&self.value);
        match result {
            Equal => other.depth.cmp(&self.depth),
            _ => result,
        }
    }
}



impl Node {
    fn new(shape: Shape, matrix: Matrix, center: A) -> Node {
        let value = valuation(shape, &matrix);
        Node {
            matrix: Rc::new(matrix),
            shape: shape,
            center: center,
            value: value,
            parent: None,
            delay: None,
            step: Start,
            depth: 0,
        }
    }
}


fn valuation(shape: Shape, matrix: &Matrix) -> uint {
        let value = matrix.iter().enumerate()
            .map(|(i, v)| point_value(shape, i as int, *v as int))
            .fold(0, |a, b| a + b);
        value as uint
}

fn point_value(shape: Shape, index: int, value: int) -> int {
    let (_, b) = shape;
    let y = b as int;
    abs(index/y - value/y) + abs((index % y) - (value % y))
}


fn swap(parent: Rc<Node>, step: Step) -> Option<Node> {
    let center = parent.center;
    let shape = parent.shape;
    let (a, b) = shape;
    let index = match step {
        Up => if center >= b {Some(center - b)} else {None},
        Down => if center / b < a - 1 {Some(center + b)} else {None},
        Left => if center % b != 0 {Some(center - 1)} else {None},
        Right => if center % b != b - 1 {Some(center + 1)} else {None},
        _ => fail!("Can't swap this step.")
    };
    match index {
        None => None,
        Some(shift) => {
            let i1 = center as int;
            let i2 = shift as int;
            let v1 = *parent.matrix.get(center as uint) as int;
            let v2 = *parent.matrix.get(shift as uint) as int;
            let old_value = parent.value as int;
            let new_value = old_value
                - (point_value(shape, i1, v1) + point_value(shape, i2, v2))
                + (point_value(shape, i1, v2) + point_value(shape, i2, v1));
            Some(Node {
                matrix: parent.matrix.clone(),
                depth: parent.depth + 1,
                parent: Some(parent.clone()),
                center: shift,
                value: new_value as uint,
                step: step,
                delay: Some((center, shift)),
                shape: parent.shape,
            })
        }
    }
}


fn force(delay_node: Rc<Node>) -> Rc<Node> {
    match delay_node.delay {
        None => delay_node,
        Some((a, b)) => {
            let mut matrix = delay_node.matrix.deref().clone();
            let mut node = delay_node.deref().clone();
            matrix.as_mut_slice().swap(a as uint, b as uint);
            node.matrix = Rc::new(matrix);
            node.delay = None;
            Rc::new(node)
        }
    }
}

fn solve_with_node(root: Rc<Node>, max_loop: uint) -> Rc<Node> {
    let mut solutions = Vec::new();
    let mut open = PriorityQueue::with_capacity(max_loop);
    let mut close = HashSet::with_capacity(max_loop);
    open.push(root.clone());
    solutions.push(root.clone());
    let mut solution_value = root.value;
    for _ in range(0, max_loop) {
        match open.pop() {
            None => break,
            Some(delay_node) => {
                let node = force(delay_node);
                let value = node.value;
                if value == solution_value {solutions.push(node.clone());}
                else if value < solution_value {
                    solution_value = value;
                    solutions.clear();
                    solutions.push(node.clone());
                }
                let matrix = node.matrix.deref();
                if !close.contains(matrix) {
                    close.insert(matrix.clone());
                    for step in [Up, Right, Down, Left].iter() {
                        match swap(node.clone(), *step) {
                            Some(new) => open.push(Rc::new(new)),
                            None => ()
                        }
                    }
                }
            },
        };
    }
    solutions.sort_by(|a, b| b.depth.cmp(&a.depth));
    println!("solution num {}", solutions.len());
    match solutions.pop() {
        None => fail!("Error solve funtion not solution."),
        Some(solution) => solution,
    }
}


fn solve(shape: Shape, matrix: Matrix, max_selection: uint) -> Node {
    let max_loop = 10000u;
    for center in range(matrix.len()) {
        let root = Rc::new(Node::new(shape, matrix, 0));
        solve_with_node(root, max_loop).deref().clone()
    }
}



fn parse() -> (Shape, uint) {
    let args: Vec<String> = os::args();
    if args.len() < 4 {fail!("Lack argument.")}
    let nums: Vec<uint> = args.slice(1, args.len()).iter().map(
        |x| match from_str(x.as_slice().trim()) {
            Some(n) => n,
            None => fail!("Command line parse error, can't convert to int"),
        }
    ).collect();
    let first = *nums.get(0) as A;
    let second = *nums.get(1) as A;
    let third = *nums.get(2);
    ((first, second), third)
}


fn get_matrix(shape: Shape) -> Matrix {
    let (x, y) = shape;
    let size = x as uint * y as uint;
    let mut matrix = Vec::from_fn(size, |id| id as A);
    task_rng().shuffle(matrix.as_mut_slice());
    matrix.shrink_to_fit();
    matrix
}

fn get_pos(shape: Shape, n: A) -> uint {
    let (_, b) = shape;
    let x = b as uint;
    let i = n as uint;
    (i % x) * 0x10 + (i / x)
}

fn print_matrix(shape: Shape, matrix: &Matrix) {
    let (_, b) = shape;
    let mut i = 0;
    for x in matrix.iter() {
        print!(" {:02X}", get_pos(shape, *x));
        if (i+1) % b == 0 {print!("\n\n")}
        i += 1;
    }
}


fn main() {
    let (shape, max_selection) = parse();
    let matrix = get_matrix(shape);
    println!("Input : ")
    print_matrix(shape, &matrix);
    println!("solve...")
    let solution = solve(shape, matrix, max_selection);
    println!("Solution : ");
    print_matrix(shape, solution.matrix.deref());
    println!("depth : {}", solution.depth);
}
