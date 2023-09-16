'''
A system regularly registers tests, students, their test submissions and the
grades each test has received.
Students can submit more than one test per day, and can submit the same test
more than once.
Tests can optionally be graded, with grades ranging from 0-100. If a test is
graded with a 0, it was deemed invalid.

We need to know:

The number of unique students who submitted at least 1 test each day, for the
last 15 days of data available.
The number of unique students who submitted at least 1 valid test each day, for
 the last 15 days of data available.
The student with the most submissions for each day of the last 15 days of data
available. If there are two or more students with the same results, print the
student with the lowest ID.
The average grade for each test. If a student has submitted just once, consider
that grade regardless of its value. If the student submitted the same test
multiple times, give preference to the last valid grade.

The solution can be developed in any programming language you'd like
(Python, SQL, Ruby, etc.).
It will have to ingest the data and print on the console the answers for the
problems above.

You should provide the script (or scripts) you developed, and a Dockerfile for
us to run your script.
'''

# %%
# Import of libraries

import pandas as pd

# %%
# First of all, data is read

grades = pd.read_csv('grades.csv')
students = pd.read_csv('grades.csv')
submissions = pd.read_csv('submissions.csv')
tests = pd.read_csv('tests.csv')

# %%
'''
Two questions ask for information related to the last 15 days of data
available, so we are getting these dates
'''

# A Date column is obtained for future use
submissions['submission_date'] = (
    pd.to_datetime(submissions['submission_time']).dt.date
    )

# Available dates are obtained and ordered
last_15_days = (
    submissions['submission_date'].sort_values(ascending=False).unique()
    )

# With this, min date of last 15 availables dates is obtained
min_15_days = last_15_days[14]

# %%
# For the first question, the only table needed is submissions
# First, only data from last 15 available days will remain

submissions_15 = submissions.loc[
    submissions['submission_date'] >= min_15_days
    ]

# At this point, only non duplicated student_id and submission_date will remain

unique_submissions_15 = (
    submissions_15[['student_id', 'submission_date']].drop_duplicates()
    )

# The groupby function is used to obtain the number of students who have
# submitted at leat 1 test each day

submission_per_day = (
    unique_submissions_15.groupby('submission_date', as_index=False).count()
    )
submission_per_day = submission_per_day.rename(
    columns={'student_id': 'test_number'}
    )

print('The answer to first problem is')
print(submission_per_day)
print()

# %%
# For the second question, it is asked to obtain the students who submitted at
# least one valid test, so the use of the grades table is needed

# A test is invalid if its grade is a 0, so grades table is filtered into
# valid_grades

valid_grades = grades.loc[grades['grade'] > 0]

# valid_grades is merged with submissions_15

valid_submissions_15 = submissions_15.merge(valid_grades, on='submission_id')

# The step of keeping not duplicated student_id and submission_date is repeated

unique_valid_submissions_15 = (
    valid_submissions_15[['student_id', 'submission_date']].drop_duplicates()
    )

# The groupby function is used to obtain the number of students who have
# submitted at leat 1 valid test each day

valid_submissions_per_day_15 = (
    submissions_15[['submission_date']]
    .sort_values('submission_date')
    .drop_duplicates()
    .merge(
        unique_valid_submissions_15
        .groupby('submission_date', as_index=False).count(),
        on=['submission_date'],
        how='left'
        )
    .fillna(0)
    )
valid_submissions_per_day_15 = valid_submissions_per_day_15.assign(
    student_id=valid_submissions_per_day_15['student_id'].astype(int)
    )
valid_submissions_per_day_15 = valid_submissions_per_day_15.rename(
    columns={'student_id': 'test_number'}
    )

print('The answer to second problem is')
print(valid_submissions_per_day_15)
print()

# %%
# Third question is asking for the student with most submissions for each day
# of the last 15 days of data available, keeping the lowest ID student in case
# of a draw

submissions_per_student_15 = (
    submissions_15
    .groupby(['submission_date', 'student_id'], as_index=False)
    .agg({'submission_id': 'count'})
    )

# Max number of submissions per student is obtained
max_submissions_per_date_15 = (
    submissions_per_student_15
    .groupby('submission_date', as_index=False)
    .agg({'submission_id': 'max'})
    )

# Both tables are merged
max_submissions_per_date_15 = max_submissions_per_date_15.merge(
    submissions_per_student_15, on=['submission_date', 'submission_id']
    )

# Table is ordered by date and student_id
max_submissions_per_date_15 = max_submissions_per_date_15.sort_values([
    'submission_date', 'student_id'
    ])
max_submissions_per_date_15 = max_submissions_per_date_15.rename(
    columns={'submission_id': 'test_number'}
    )

# Only min student_id remains
print('The answer to third problem is')
print(
      max_submissions_per_date_15.drop_duplicates(
          subset=['submission_date', 'test_number']
          )
      .reset_index(drop=True)
      )
print()

# %%
# Final question ask for the average grade for each test
# If a student has submitted a test just once, keep that grade
# If a student has submitted a test several times, keep last valid grade

# First, students' test are divided into those with one try
# and those with more

test_submissions = (
    submissions
    .groupby(['test_id', 'student_id'], as_index=False)
    ['submission_id']
    .count()
    )

one_test = test_submissions.loc[test_submissions['submission_id'] == 1]
sev_test = test_submissions.loc[test_submissions['submission_id'] > 1]

# Those tests with several tries, are merged with valid_grades, to get the last
# valid test

sev_test_submissions = (
    sev_test.drop('submission_id', axis=1)
    .merge(submissions, on=['test_id', 'student_id'])
    .merge(valid_grades, on=['submission_id'])
    .sort_values('submission_time', ascending=False)
    .drop_duplicates(subset=['test_id', 'student_id'])
    )

# If a student has done the same test several times, but with a invalid grade,
# that grade is also added, as only valid grades were kept in last step

sev_test_submissions = (
    sev_test[['test_id', 'student_id']].merge(
        sev_test_submissions[['test_id', 'student_id', 'grade']],
        on=['test_id', 'student_id'],
        how='left'
        )
    .fillna(0)
    )

# Next step is adding those with just a test
one_test_submission = (
    one_test.drop('submission_id', axis=1)
    .merge(submissions, on=['test_id', 'student_id'])
    .merge(grades, on=['submission_id'])
    [['test_id', 'student_id', 'grade']]
    )

graded_test = pd.concat([one_test_submission, sev_test_submissions])

# Averages of each test are obtained
print('The answer to last problem is')
print(
    graded_test.groupby('test_id', as_index=False)['grade'].mean()
    .merge(tests, on='test_id')
    [['test_name', 'grade']]
    )
print()
