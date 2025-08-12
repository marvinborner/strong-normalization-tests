import           Data.List                      ( (!?) )
import           Data.List.Split                ( splitOn )
import           Data.Map                       ( Map )
import qualified Data.Map                      as Map

data Term = Abs Int Term | App Term Term | Var Int
data HTerm = HAbs (HTerm -> HTerm) | HApp HTerm HTerm | HVar Int
data DTerm = DAbs DTerm | DApp DTerm DTerm | DIdx Int deriving Eq

app :: HTerm -> HTerm -> HTerm
app (HAbs f) = f
app f        = HApp f

higher :: Term -> HTerm
higher = go Map.empty
 where
  go env (Var x) = case Map.lookup x env of
    Just v -> v
    _      -> HVar x
  go env (Abs n t) = HAbs $ \x -> go (Map.insert n x env) t
  go env (App a b) = app (go env a) (go env b)

lower :: HTerm -> Term
lower = go 0
 where
  go _ (HVar x  ) = Var x
  go d (HAbs t  ) = Abs d $ go (d + 1) (t (HVar d))
  go d (HApp a b) = App (go d a) (go d b)

reduce :: Term -> Term
reduce = lower . higher

toDeBruijn :: Term -> DTerm
toDeBruijn = go []
 where
  go vs (Var x) = DIdx $ case vs !? x of
    Just x  -> x
    Nothing -> x
  go vs (Abs n t) = DAbs $ go (n : vs) t
  go vs (App a b) = DApp (go vs a) (go vs b)


fromBinary :: String -> Term
fromBinary = fst . go [] 0
 where
  go env n inp = case inp of
    '0' : '0' : rst -> do
      let (e, rst1) = go (n : env) (n + 1) rst
      (Abs n e, rst1)
    '0' : '1' : rst -> do
      let (a, rst1) = go env n rst
      let (b, rst2) = go env n rst1
      (App a b, rst2)
    '1' : rst -> do
      let idx = length (takeWhile (== '1') rst)
      case env !? idx of
        Just v  -> (Var v, drop (idx + 1) rst)
        Nothing -> error "open term"
    _ -> error $ "invalid " ++ inp

main :: IO ()
main = do
  tests <- readFile "tests"
  let ls = lines tests
  reduced <- flip mapM ls $ \line -> do
    let bruijn : tests : _ = splitOn ": " line
    let left : right : _   = splitOn " - " tests
    let left'              = reduce $ fromBinary left
    let right'             = reduce $ fromBinary right
    putStrLn $ "reducing: " <> bruijn
    return (bruijn, toDeBruijn left' == toDeBruijn right')
  let failing = filter (not . snd) reduced
  putStrLn $ "failing: " <> show failing
