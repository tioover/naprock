use std::sync::Arc;
use std::num::abs;
use std::collections::HashSet;
use std::rand::{task_rng, Rng};
use std::comm;

type M = u8;
type N = int;
type Matrix = Arc<Vec<M>>;
type Shape = (N, N);
type Value = int;
static X: N = 10;
static Y: N = 10;
static MAX_LOOP: uint = 100000u;
static TASK_NUM: uint = 6;
static BASE: uint = 1000;
static THRESHOLD: uint = 2000;


#[deriving(Clone)]
enum Step
{
    Select,
    Start,
    Left,
    Right,
    Up,
    Down,
}

#[deriving(Clone)]
struct Node
{
    matrix: Matrix,
    shape: Shape,
    center: N,
    value: Value,
    parent: Option<Arc<Node>>,
    step: Step,
    depth: uint,
}


impl Node
{
    fn print(&self)
    {
        let (x, y) = self.shape;
        let matrix = self.matrix.as_slice();
        for i in range(0, x as uint) {
            let j = y as uint;
            println!("{}", matrix.slice(i*j, i*j+j));
        }
        println!("value: {} center: [{}] {} step: {}\n",
                 self.value, self.center, (self.center / y + 1, self.center % y + 1), self.depth);
    }
}


fn point_value(index: uint, value: u8, shape: Shape) -> int {
    let i = index as int;
    let v = value as int;
    let (_, b) = shape;
    let y = b as int;
    abs(i/y - v/y) + abs((i % y) - (v % y))
}


fn valuation(matrix: &Matrix, shape: Shape) -> Value
{
    let mut value: Value = 0;
    for i in range(0, matrix.len()) {
        value += point_value(i, *matrix.get(i), shape)
    }
    value
}


fn get_shift(step: Step, shape: Shape, center: N) -> Option<N> {
    let (x, y) = shape;
    match step {
        Up => if center >= y {Some(center - y)} else {None},
        Down => if center < x*y - y {Some(center + y)} else {None},
        Left => if center % y != 0 {Some(center - 1)} else {None},
        Right => if (center + 1) % y != 0 {Some(center + 1)} else {None},
        _ => fail!("turn arg error")
    }
}

fn turn(parent: Arc<Node>, step: Step) -> Option<Arc<Node>>
{
    let shape = parent.shape;
    let center = parent.center;
    match get_shift(step, shape, center) {
        None => None,
        Some(shift) => {
            let mut matrix = parent.matrix.deref().clone();
            {
                let matrix_slice = matrix.as_mut_slice();
                matrix_slice.swap(center as uint, shift as uint);
            }
            let matrix = Arc::new(matrix);
            Some(
                Arc::new(
                    Node {
                        value: valuation(&matrix, parent.shape),
                        matrix: matrix,
                        shape: shape,
                        parent: Some(parent.clone()),
                        center: shift,
                        step: step,
                        depth: parent.depth + 1,
                    }
                )
            )
        }
    }
}


fn insert(open: &mut Vec<Arc<Node>>, node: Arc<Node>) -> ()
{
    let value = node.value;
    let len = open.len();

    if len == 0 || open.get(len-1).value >= value {
        open.push(node);
    }
    else if open.get(0).value < value {
        open.insert(0, node);
    }
    else {
        for i in range(0, len) {
            let n = len-1-i;
            if open.get(n).value >= node.value {
                open.insert(n, node);
                break;
            }
        }
    }
}

fn add(open: &mut Vec<Arc<Node>>, node: Arc<Node>) -> () {
    let mut shift = [Up, Down, Left, Right];
    task_rng().shuffle(shift);
    for step in shift.iter() {
        match turn(node.clone(), *step) {
            None => (),
            Some(new_node) => insert(open, new_node),
        };
    };
}


fn is_update(raw: &Arc<Node>, new: &Arc<Node>) -> bool {
    (new.value < raw.value) || (new.value == raw.value && new.depth < raw.depth)
}


fn solve_with_node(
        root: Arc<Node>,
        open: &mut Vec<Arc<Node>>,
        close: &mut HashSet<Vec<u8>>
    ) -> Arc<Node>
{
    let mut update = 0;
    let mut solution = root.clone();
    open.push(root);
    for i in range(0, MAX_LOOP) {
        if i > BASE && i - update > THRESHOLD {break;}
        match open.pop() {
            None => {println!("ERROR: Open empty."); break},
            Some(node) => {
                let value = node.value;
                if value == 0 {return node;}
                else if close.contains(node.matrix.deref()) {continue;}
                else {close.insert(node.matrix.deref().clone());}
                if is_update(&solution, &node) {
                    solution = node.clone();
                    update = i;
                };
                add(open, node);
            }
        }
    }
    solution
}

fn solve_loop(root: Arc<Node>) -> Arc<Node>
{
    let (tx, rx): (Sender<Arc<Node>>, Receiver<Arc<Node>>) = comm::channel();
    let (x, y) = root.shape;
    let len = (x*y) as uint;
    for id in range(0, TASK_NUM) {
        let task_tx = tx.clone();
        let new = root.clone();
        spawn(proc() {
            let mut solutions = Vec::with_capacity(len/2);
            let mut open: Vec<Arc<Node>> = Vec::with_capacity(MAX_LOOP * 3);
            let mut close = HashSet::with_capacity(MAX_LOOP * 3);
            for i in range(0, len) {
                if i % TASK_NUM != id {continue}
                let mut now = new.deref().clone();
                now.center = i as N;
                now.parent = Some(new.clone());
                now.step = Select;
                solutions.push(
                    solve_with_node(
                        Arc::new(now),
                        &mut open,
                        &mut close
                    )
                );
                open.clear();
                close.clear();
            }
            solutions.sort_by(|a, b| b.value.cmp(&a.value));
            match solutions.pop() {
                None => fail!("error in thread return"),
                Some(solution) => task_tx.send(solution),
            }
        });
    }
    let mut pre_solutions = Vec::with_capacity(len);
    for _ in range(0, TASK_NUM) {
        pre_solutions.push(rx.recv());
    }
    pre_solutions.sort_by(|a, b| b.value.cmp(&a.value));
    match pre_solutions.pop() {
        Some(solution) => solution,
        _ => fail!("error in solve_loop return.")
    }
}


fn solve(matrix: Matrix, shape: Shape, select_num: uint) -> Arc<Node>
{
    let mut root = Arc::new(Node {
        value: valuation(&matrix, shape),
        matrix: matrix,
        shape: shape,
        center: 0,
        depth: 0,
        step: Start,
        parent: None,
    }); // init
    for i in range(0, select_num) {
        root = solve_loop(root);
        if root.value == 0 {break;}
        println!("{}", i);
        root.print();
    }
    root
}


fn main()
{
    let mut matrix = Vec::from_fn((X*Y) as uint, |id| id as u8);
    {
        let m = matrix.as_mut_slice();
        task_rng().shuffle(m);
    }
    let solution = solve(Arc::new(matrix), (X, Y), 16);
    solution.print();
}
