import unittest
import data_processing
import pandas as pd

class TestDataProcessing(unittest.TestCase):
    d = {
        'col1': [1, 2, 3, 4], 
        'col2': ['3,1', '4,5', '8,4', '3,4'],
        'col3': ['a', 'b', 'c', 'e']
    }
    df_test = pd.DataFrame(data=d)


    def test_df_decimal_sep(self):
        '''Test conversion of data having ',' as separator to float.'''
        df_decimal = data_processing.DataProcessing.df_decimal_sep(
            self.df_test)
        self.assertIsInstance(df_decimal['col2'][2], float)

    def test_numeric_columns(self):
        '''Test numeric column selection.'''
        df_decimal = data_processing.DataProcessing.df_decimal_sep(
            self.df_test)
        df_numeric = data_processing.DataProcessing.numeric_columns(
            df_decimal)
        d_exp = {
            'col1': [1.0, 2.0, 3.0, 4.0], 
            'col2': [3.1, 4.5, 8.4, 3.4],
        }
        expected = pd.DataFrame(data=d_exp)
        pd.testing.assert_frame_equal(df_numeric, expected)
      

if __name__ == '__main__':
    unittest.main()
